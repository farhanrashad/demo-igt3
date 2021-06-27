# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

import json
from lxml import etree

class OPPenaltyEntry(models.Model):
    _name = 'op.penalty.entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Penalty Entry'
    
    def _get_default_stage_id(self):
        return self.env['op.penalty.stage'].search([('stage_category','=','draft')], order='sequence', limit=1)
    
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', copy=False, required=True, index=True, default=lambda s: s.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, 
                                  default=lambda self: self.env.company.currency_id.id)

    text = fields.Text()
        
    date_entry = fields.Datetime('Entry Date', required=True, index=True, copy=False, default=fields.Datetime.now,)

    penalty_type_id = fields.Many2one('op.penalty.type', string='Entry Type', index=True, required=True, readonly=True, )
    stage_id = fields.Many2one('op.penalty.stage', string='Stage', compute='_compute_stage_id', store=True, readonly=False, ondelete='restrict', tracking=True, index=True, default=_get_default_stage_id, copy=False)
    stage_category = fields.Selection(related='stage_id.stage_category')
                                   

    penalty_entry_line = fields.One2many('op.penalty.entry.line', 'penalty_entry_id', string='Entry Line', copy=True, auto_join=True)
    
    #account related fields
    journal_id = fields.Many2one('account.journal',related='penalty_type_id.journal_id')
    
    #Header Fields
    has_partner = fields.Selection(related="penalty_type_id.has_partner")
    has_invoice = fields.Selection(related="penalty_type_id.has_invoice")
    partner_id = fields.Many2one('res.partner',  String="Supplier")
    invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True)

    amount_total = fields.Float(string='Amount Total')
    confirmed_amount_total = fields.Float(string='Confirmed Amount Total')
    month  = fields.Char(string='Month')
    amount_total_all = fields.Float(string="Total Amount")
    ref = fields.Char('Reference', copy=False)
    
    #Line Item fields
    has_hse_fields = fields.Selection(related="penalty_type_id.has_hse_fields")
    has_pm_fields = fields.Selection(related="penalty_type_id.has_pm_fields")
    has_sla_fields = fields.Selection(related="penalty_type_id.has_sla_fields")
    has_spmrf_fields = fields.Selection(related="penalty_type_id.has_spmrf_fields")
    

    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    
    @api.depends('penalty_type_id')
    def _compute_stage_id(self):
        for entry in self:
            if entry.penalty_type_id:
                if entry.penalty_type_id not in entry.stage_id.penalty_type_ids:
                    entry.stage_id = entry.stage_find(entry.penalty_type_id.id, [('fold', '=', False), ('stage_category', '=', 'draft')])
            else:
                entry.stage_id = False
    
    def stage_find(self, section_id, domain=[], order='sequence'):
        section_ids = category_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('penalty_type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('penalty_type_ids', '=', section_id))
        search_domain += list(domain)
        return self.env['op.penalty.stage'].search(search_domain, order=order, limit=1).id

           
    
    @api.depends('penalty_entry_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for entry in self:
            invoices = entry.mapped('penalty_entry_line.invoice_lines.move_id')
            entry.invoice_ids = invoices
            entry.invoice_count = len(invoices)

    def unlink(self):
        for r in self:
            if r.stage_category != 'draft' or r.stage_category == 'cancel':
                raise UserError(
                    "You can not delete records other than in draft/cancelled state.")
        for rec in self:
            if rec.stage_id.stage_category != 'draft' or rec.stage_id.stage_category != 'cancel':
                raise UserError(
                    "You can not delete records other than in draft/cancelled state.")
        return super(OPPenaltyEntry, self).unlink()
    
   
    def button_draft(self):
        self.write({'stage_id': 1})
        return {}
    
    def action_confirm(self):
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        return {}

    def action_refuse(self):
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        
        
    def action_submit(self):
        self.ensure_one()
        if not self.penalty_entry_line:
            raise UserError(_("You cannot submit requisition '%s' because there is no product line.", self.name))
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'stage_id': 'cancel'})
      
    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        #move_type = self._context.get('default_move_type', 'in_invoice')
        move_type = 'in_invoice'
        journal = self.penalty_type_id.journal_id.id
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.name,
            'move_type': move_type,
            'journal_id': journal,
            #'narration': self.notes,
            'invoice_date': fields.Datetime.now(),
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': self.partner_id.id,
            #'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            #'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals
    
    
    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
    
    def create_advance_expense(self):
        res = self._create_penalty_invoice()
        #return self.action_subscription_invoice()
        
    def create_penalty_invoice(self):
        res = self._create_penalty_invoice()
        #return self.action_subscription_invoice()
    
    def _create_penalty_invoice(self):
        invoice = self.env['account.move']
        lines_data = []
        
        if self.penalty_type_id.has_penalty_fields != 'no':
            for line in self.penalty_entry_line:
                lines_data.append([0,0,{
                    'name': self.name + ' , ' + line.job_scope + ' , ' + line.car_details.name + ' , ' + str(self.duration_from) + ' - ' + str(self.duration_to),
                    'penalty_entry_line_id': line.id,
                    'price_unit': line.amount or 0.0,
                    'quantity': 1.0,
                    'account_id' : line.job_scope_account.id,
                    'tax_ids': [(self.taxe_ids.id)] if self.taxe_ids.id else False,
                }])
            invoice.create({
                'move_type': 'in_invoice',
                'penalty_entry_id': self.id,
                'invoice_date': fields.Datetime.now(),
                'partner_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'journal_id': self.penalty_type_id.journal_id.id,
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
                'narration': self.name,
                'invoice_user_id': self.user_id.id,
                'invoice_line_ids':lines_data,
            })
            invoice.create({
                'move_type': 'in_invoice',
                'penalty_entry_id': self.id,
                'invoice_date': fields.Datetime.now(),
                'partner_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'journal_id': self.penalty_type_id.journal_id.id,
                'invoice_origin': self.name,
                'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
                'narration': self.name,
                'invoice_user_id': self.user_id.id,
                'invoice_line_ids':lines_data,
            })
            

        return invoice
    
    
class OPPenaltyEntryLine(models.Model):
    _name = 'op.penalty.entry.line'
    _description = 'penalty Entry Line'
    
    penalty_entry_id = fields.Many2one('op.penalty.entry', string='Penalty Entry', required=True, ondelete='cascade', index=True, copy=False)
    company_id = fields.Many2one(
        string='Company', related='penalty_entry_id.company_id',
        store=True, readonly=True, index=True)
    currency_id = fields.Many2one(related='penalty_entry_id.currency_id', store=True, string='Currency', readonly=True)

    invoice_lines = fields.One2many('account.move.line', 'penalty_entry_line_id', string="Bill Lines", readonly=True, copy=False)

    project_id = fields.Many2one('project.project', string='Site')
    name = fields.Char(stirng='Description')
    penalty_percent = fields.Float(string='% Penalty')
    service_charge = fields.Float(string='Service Charge')
    confirmed_amount = fields.Float(string='Confirmed Amount')
    amount = fields.Float(string='Penalty Amount')
    
    #sla
    service_class = fields.Selection([
        ('a', 'Critical Site'), 
        ('b', 'Class B'), 
        ('c', 'Class C')], default='a', string='Classification')
    service_level = fields.Selection([
        ('critical', 'Critical'), 
        ('major', 'Major'), 
        ('minor', 'Minor'), 
        ('normal', 'Normal')], default='normal', string='Service Level')
    uptime = fields.Float(string='Uptime', default=0.0)
    #occurence
    #sow
    penalty_sow_type_id = fields.Many2one('op.penalty.config.sow.type', string='SOW Type')
    penalty_sow_id = fields.Many2one('op.penalty.config.sow', string='SOW')
    frequency = fields.Char(related='penalty_sow_id.frequency')
    sow_deduct_type = fields.Selection([
        ('a', 'A'), 
        ('b', 'B'), 
        ], default='a', string='Deduction Type')
    
    description = fields.Text(string="Remarks")
    
    
    
    
    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            'name': '%s: ' % (self.penalty_entry_id.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.product_qty,
            'price_unit': self.price_unit,
            #'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'penalty_entry_line_id': self.id,
            'project_id': self.project_id.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res
    
    

