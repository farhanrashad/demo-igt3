# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta

import json
from lxml import etree

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'),('12', 'Dec')]

class CustomEntry(models.Model):
    _name = 'account.custom.entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Custom Entry'
    _order = "date_entry desc"
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        custom_entry_type_id = self.env.context.get('default_custom_entry_type_id')
        if not custom_entry_type_id:
            return False
        return self.stage_find(custom_entry_type_id, [('fold', '=', False)])
    
    def _get_default_currency_id(self):
        default_currency_id = self.env.context.get('default_currency_id')
        return [default_currency_id] if default_currency_id else None
    
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date_entry = fields.Datetime(string='Entry Date', required=True, index=True, copy=False, default=fields.Datetime.now,)
    date_entry_month = fields.Selection(MONTH_LIST, string='Month')
    date_entry_year = fields.Char(string='Year', compute='_compute_entry_year', store=True)

    date_submit = fields.Datetime('Submission Date', readonly=False)
    date_approved = fields.Datetime('Approved Date', readonly=False)

    user_id = fields.Many2one('res.users', string="Request Owner",check_company=True, domain="[('company_ids', 'in', company_id)]", default=lambda self: self.env.user, required=True,readonly=True, )
    company_id = fields.Many2one('res.company', 'Company', copy=False, required=True, index=True, default=lambda s: s.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=_get_default_currency_id)
    
    stage_id = fields.Many2one('account.custom.entry.stage', string='Stage', compute='_compute_stage_id', store=True, readonly=False, ondelete='restrict', tracking=True, index=True, default=_get_default_stage_id, domain="[('custom_entry_type_ids', '=', custom_entry_type_id)]", copy=False)
    custom_entry_type_id = fields.Many2one('account.custom.entry.type', string='Entry Type', index=True, required=True, readonly=True,)
    
    amount_advanced_total = fields.Float('Total Advanced', compute='_amount_all')
    amount_total = fields.Float('Total Amount', compute='_amount_all')
    amount_balance = fields.Float('Balance', compute='_amount_all')
 
    custom_entry_line = fields.One2many('account.custom.entry.line', 'custom_entry_id', string='Entry Line', copy=True, auto_join=True,)
    
    @api.onchange('custom_entry_type_id')
    def _onchange_entry_type(self):
        for entry in self:
            entry.currency_id = entry.custom_entry_type_id.currency_id.id
    
    #account related fields
    stage_category = fields.Selection(related='stage_id.stage_category')
    account_entry_type = fields.Char(string='Accounting Entry Type', compute='_account_entry_type', )
    expense_advance = fields.Boolean(related='custom_entry_type_id.expense_advance')
    journal_id = fields.Many2one('account.journal',related='custom_entry_type_id.journal_id')
    journal_type = fields.Selection(related='custom_entry_type_id.journal_type')
    
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='cascade', change_default=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    
    
    #Header optional fields
    has_partner = fields.Selection(related="custom_entry_type_id.has_partner")
    has_ref = fields.Selection(related="custom_entry_type_id.has_ref")
    has_supplier_bill = fields.Selection(related="custom_entry_type_id.has_supplier_bill")
    has_period = fields.Selection(related="custom_entry_type_id.has_period")
    has_attachment = fields.Selection(related="custom_entry_type_id.has_attachment")
    has_description = fields.Selection(related="custom_entry_type_id.has_description")
    has_purchase_requisition = fields.Selection(related="custom_entry_type_id.has_purchase_requisition")
    has_purchase = fields.Selection(related="custom_entry_type_id.has_purchase")
    has_picking = fields.Selection(related="custom_entry_type_id.has_picking")
    has_invoice = fields.Selection(related="custom_entry_type_id.has_invoice")
    
    ref = fields.Char('Reference', copy=False)
    supplier_bill_ref = fields.Char(string='Supplier Bill Ref.')
    attachment1 = fields.Boolean(string='Attachment 1')
    description = fields.Text(string='Description')
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Requisition", check_company=True, ondelete='cascade')
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", check_company=True, ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string="Invoice Reference", check_company=True, ondelete='cascade')
    picking_id = fields.Many2one('stock.picking', string="Picking Reference", check_company=True, ondelete='cascade')
    
    
    #optional line items fields
    has_line_period = fields.Selection(related="custom_entry_type_id.has_line_period")
    has_project = fields.Selection(related="custom_entry_type_id.has_project")
    has_analytic = fields.Selection(related="custom_entry_type_id.has_analytic")
    has_product = fields.Selection(related="custom_entry_type_id.has_product")
    has_employee = fields.Selection(related="custom_entry_type_id.has_employee")
    has_supplier = fields.Selection(related="custom_entry_type_id.has_supplier")
    has_advanced = fields.Selection(related="custom_entry_type_id.has_advanced")
    
    #application optional fields
    has_rent_vechile = fields.Selection(related="custom_entry_type_id.has_rent_vechile")
    has_travel = fields.Selection(related="custom_entry_type_id.has_travel")
    has_hotel = fields.Selection(related="custom_entry_type_id.has_hotel")
    has_electricity = fields.Selection(related="custom_entry_type_id.has_electricity")
    has_fuel_drawn = fields.Selection(related="custom_entry_type_id.has_fuel_drawn")
    has_fuel_filling = fields.Selection(related="custom_entry_type_id.has_fuel_filling")
    
    #application common extra fields for hotel/accomodation
    customer_type = fields.Selection([('local', 'Local'), ('expat', 'Expat')], string='Customer Type')
    date_effective = fields.Date(string='Effective Date')
    date_subscription = fields.Date(string='Date of Subscription')
    
    #fleet/rent vehicle extra fields
    f_duration_from = fields.Date(string='Duration')
    f_duration_to = fields.Date(string='')
    
    #travel fields
    t_travel_by = fields.Selection([
        ('ticket', 'Flight Ticket'),
        ('Vehicle', 'Vehicle Rental')],
        string='Travel By', default='ticket')
    
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_count = fields.Integer(compute="_compute_all_moves", string='Bill Count', copy=False, default=0,)
    move_count = fields.Integer(compute="_compute_all_moves", string='Move Count', copy=False, default=0)

    
    @api.depends('date_entry')
    def _compute_entry_year(self):
        for entry in self:
            entry_year = entry.date_entry
            entry.date_entry_year = entry_year.year

    @api.depends('stage_id')
    def _account_entry_type(self):
        for entry in self:
            if entry.stage_id.next_stage_id:
                entry.account_entry_type = entry.stage_id.next_stage_id.account_entry_type
            else:
                entry.account_entry_type = 'none'
            
   
                
    @api.depends('custom_entry_type_id')
    def _compute_stage_id(self):
        for entry in self:
            if entry.project_id:
                if entry.custom_entry_type_id not in entry.stage_id.custom_entry_type_ids:
                    entry.stage_id = entry.stage_find(entry.custom_entry_type_id.id, [
                        ('fold', '=', False)])
            else:
                entry.stage_id = False
    
    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('custom_entry_type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('custom_entry_type_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['account.custom.entry.type'].search(search_domain, order=order, limit=1).id
    
    
    def stage_find(self, section_id, domain=[], order='sequence'):
        section_ids = category_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('custom_entry_type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('custom_entry_type_ids', '=', section_id))
        search_domain += list(domain)
        return self.env['account.custom.entry.stage'].search(search_domain, order=order, limit=1).id
    
    @api.depends('custom_entry_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for entry in self:
            invoices = entry.mapped('custom_entry_line.invoice_lines.move_id')
            entry.invoice_ids = invoices
            #entry.invoice_count = len(invoices)
    
    @api.depends('custom_entry_line.invoice_lines.move_id')
    def _compute_all_moves(self):
        Move = self.env['account.move']
        can_read = Move.check_access_rights('read', raise_exception=False)
        for move in self:
            move.invoice_count = can_read and Move.search_count([('custom_entry_id', '=', move.id),('move_type', '=', 'in_invoice'),('journal_id', '=', move.custom_entry_type_id.journal_id.id)]) or 0
            move.move_count = can_read and Move.search_count([('custom_entry_id', '=', move.id),('move_type', '=', 'entry'),('journal_id', '=', move.custom_entry_type_id.journal_id.id)]) or 0

   
    def _amount_all(self):
        adv = tot = 0
        for line in self.custom_entry_line:
            tot += line.price_subtotal
            adv += line.advance_subtotal
        self.amount_advanced_total = adv
        self.amount_total = tot
        self.amount_balance = tot - adv
        
    def button_draft(self):
        self.write({'stage_id': self.next_stage_id.id})
    
    def button_submit(self):
        #self.ensure_one()
        for order in self.sudo():
            group_id = order.custom_entry_type_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to submit requisition in category '%s'.", order.custom_entry_type_id.name))
            if not order.custom_entry_line:
                raise UserError(_("You cannot submit transaction '%s' because there is no line.", self.name))
           
        self.update({
            'date_submit' : fields.Datetime.now(),
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        
    def button_confirm(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to approve '%s'.", order.stage_id.name))
                    
        self.update({
            'date_approved' : fields.Datetime.now(),
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        
    def button_done(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to close '%s'.", order.stage_id.name))
                    
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        
    def button_refuse(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to refuse '%s'.", order.stage_id.name))
        if self.prv_stage_id:
            self.update({
                'stage_id' : self.stage_id.prv_stage_id.id,
            })

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        stage_id = self.env['account.custom.entry.stage'].search([('custom_entry_type_ids','=',self.custom_entry_type_id.id)],limit=1)
        self.update({
            'stage_id': stage_id.id,
        })
      
    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        #move_type = self._context.get('default_move_type', 'in_invoice')
        move_type = 'in_invoice'
        journal = self.custom_entry_type_id.journal_id.id
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
        res = self._create_bill()
        #return self.action_subscription_invoice()
    
    def create_journal_entry(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to create Journal Entry '%s'.", order.stage_id.name))
        res = self._create_account_move()
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
    def _create_account_move(self):
        move = self.env['account.move']
        company = self.company_id
        lines_data = []
        debit = credit = amount = balance = 0
        counter_debit = counter_credit = counter_amount = counter_balance = 0
        for line in self.custom_entry_line:
            if self.custom_entry_type_id.counterpart_mode == 'debit':
                #credit = line.price_subtotal
                amount = line.price_subtotal * -1
            else:
                #debit = line.price_subtotal
                amount = line.price_subtotal
            balance = line.currency_id._convert(amount, company.currency_id, company, self.date_entry or fields.Date.context_today(line))
            debit = balance if balance > 0.0 else 0.0
            credit = -balance if balance < 0.0 else 0.0
                
                
            lines_data.append([0,0,{
                'name': str(self.name) + ' ' + str(line.product_id.name),
                'custom_entry_line_id': line.id,
                'account_id': self.custom_entry_type_id.account_id.id,
                'amount_currency': amount,
                'currency_id': self.currency_id.id,
                'debit': debit,
                'credit': credit,
                'partner_id': line.supplier_id.id,
                'analytic_account_id': line.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'project_id': line.project_id.id,
            }])
        if self.custom_entry_type_id.counterpart_mode == 'debit':
            #counter_debit = self.amount_total
            counter_amount = self.amount_total
        else:
            #counter_credit = self.amount_total
            counter_amount = self.amount_total * -1
            
        counter_balance = line.currency_id._convert(counter_amount, company.currency_id, company, self.date_entry or fields.Date.context_today(line))
        counter_debit = counter_balance if counter_balance > 0.0 else 0.0
        counter_credit = -counter_balance if counter_balance < 0.0 else 0.0
            
        lines_data.append([0,0,{
            'name': str(self.name),
            'custom_entry_line_id': line.id,
            'account_id': self.custom_entry_type_id.counterpart_account_id.id,
            'debit': counter_debit,
            'credit': counter_credit,
            'amount_currency': counter_amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
        }])
        move.create({
            'move_type': 'entry',
            'custom_entry_id': self.id,
            'ref':  str(self.name), 
            'date': fields.Datetime.now(),
            'currency_id': self.currency_id.id,
            'journal_id': self.custom_entry_type_id.journal_id.id,
            'narration': self.name,
            'line_ids':lines_data,
        })
        return move
    
        
    def create_bill(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to create bill '%s'.", order.stage_id.name))
        res = self._create_bill()
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        #return self.action_subscription_invoice()
    
    def _create_bill(self):
        invoice = self.env['account.move']
        lines_data = []
        for line in self.custom_entry_line:
            lines_data.append([0,0,{
                'name': str(self.name) + ' ' + str(line.product_id.name),
                'custom_entry_line_id': line.id,
                'price_unit': line.price_unit or 0.0,
                #'discount': line.discount,
                'quantity': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'product_id': line.product_id.id,
                #'tax_ids': [(6, 0, tax_ids.ids)],
                'analytic_account_id': line.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'project_id': line.project_id.id,
            }])
        invoice.create({
            'move_type': 'in_invoice',
            'custom_entry_id': self.id,
            'invoice_date': fields.Datetime.now(),
            'partner_id': self.partner_id.id,
            #'partner_shipping_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': self.custom_entry_type_id.journal_id.id,
            'invoice_origin': self.name,
            #'fiscal_position_id': fpos.id,
            'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'narration': self.name,
            'invoice_user_id': self.user_id.id,
            #'partner_bank_id': company.partner_id.bank_ids.filtered(lambda b: not b.company_id or b.company_id == company)[:1].id,
            'invoice_line_ids':lines_data,
        })
        return invoice
    
    def get_payment_count(self):
        for entry in self:
            count = self.env['account.payment'].search_count([('custom_entry_id', '=', entry.id)])
            entry.payment_count = count
        
    payment_count = fields.Integer(string='Payments', compute='get_payment_count')
    
    def action_view_payment(self):
        self.ensure_one()
        return {
         'type': 'ir.actions.act_window',
         'binding_type': 'object',
         'domain': [('custom_entry_id', '=', self.id)],
         'multi': False,
         'name': 'Payment',
         'target': 'current',
         'res_model': 'account.payment',
         'view_mode': 'tree,form',
        }
    
    def create_payment(self):
        for order in self.sudo():
            group_id = order.stage_id.group_id
            if group_id:
                if not (group_id & self.env.user.groups_id):
                    raise UserError(_("You are not authorize to create payment '%s'.", order.stage_id.name))
        vals = {
            'payment_type': 'outbound',
            'journal_id': self.custom_entry_type_id.payment_journal_id.id,
            'partner_type': 'supplier',
            'custom_entry_id': self.id,
            'partner_id': self.partner_id.id,
            'date': self.date_entry,
            'amount': self.amount_advanced_total,
        }
        payment = self.env['account.payment'].create(vals)
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        
    
   
    """
    def create_forcast_invoice(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        move_dict = {
#               'name': self.name,
              'journal_id': self.custom_entry_type_id.journal_id.id,
              'date': self.date_entry,
              'invoice_date': self.date_entry,
              'custom_entry_id': self.id,
              'partner_id': self.partner_id.id if self.partner_id.id else False,
              'move_type': 'in_invoice',
              'state': 'draft',
                   }
                        #step2:debit side entry
        debit_line = (0, 0, {
                'name': self.name +":"+ 'Forcast Advances',
                'debit': abs(self.amount_forecast),
                'credit': 0.0,
                'account_id': self.partner_id.property_account_payable_id.id,
                         })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                #step3:credit side entry
        credit_line = (0, 0, {
                  'name': self.name,
                  'debit': 0.0,
                  'credit': abs(self.amount_forecast),
                  'account_id': self.custom_entry_type_id.journal_id.default_account_id.id,
                          })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        lineid = 0
        for custom_line in self.custom_entry_line:
            lineid = custom_line.id    
        for line in move.invoice_line_ids:
            line.update({
                'custom_entry_line_id': lineid
            })
    
    def create_difference_invoice(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        move_dict = {
#               'name': self.name,
              'journal_id': self.custom_entry_type_id.journal_id.id,
              'date': self.date_entry,
              'invoice_date': self.date_entry,
              'custom_entry_id': self.id,
              'partner_id': self.partner_id.id if self.partner_id.id else False,
              'move_type': 'in_invoice',
              'state': 'draft',
                   }
                        #step2:debit side entry
        debit_line = (0, 0, {
                'name': self.name +":",
                'debit': abs(self.amount_difference),
                'credit': 0.0,
                'account_id': self.partner_id.property_account_payable_id.id,
                         })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                #step3:credit side entry
        credit_line = (0, 0, {
                  'name': self.name,
                  'debit': 0.0,
                  'credit': abs(self.amount_difference),
                  'account_id': self.custom_entry_type_id.journal_id.default_account_id.id,
                          })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        lineid = 0
        for custom_line in self.custom_entry_line:
            lineid = custom_line.id    
        for line in move.invoice_line_ids:
            line.update({
                'custom_entry_line_id': lineid
            })
        """
    
class CustomEntryLine(models.Model):
    _name = 'account.custom.entry.line'
    _description = 'Custom Entry Line'
    
    custom_entry_id = fields.Many2one('account.custom.entry', string='Custom Entry', required=True, ondelete='cascade', index=True, copy=False)
    note = fields.Char(string='Description')
    stage_category = fields.Selection(related='custom_entry_id.stage_category', readonly=True)
    date_entry = fields.Datetime(related='custom_entry_id.date_entry')
    date_entry_period = fields.Char(string='Month')
    
    company_id = fields.Many2one(
        string='Company', related='custom_entry_id.company_id',
        store=True, readonly=True, index=True)
    currency_id = fields.Many2one(related='custom_entry_id.currency_id', store=True, string='Currency', readonly=True)

    invoice_lines = fields.One2many('account.move.line', 'custom_entry_line_id', string="Bill Lines", readonly=True, copy=False)

    #Project   
    project_id = fields.Many2one('project.project', string="Project", check_company=True, ondelete='cascade')
    state_id = fields.Many2one('res.country.state', compute='_compute_state', string='Region', ondelete='cascade')
    analytic_account_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account',ondelete='cascade')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', ondelete='cascade')
    
    #employee
    employee_id = fields.Many2one('hr.employee',string="Employee")
    supplier_id = fields.Many2one('res.partner',string="Supplier")
    
    #Product
    product_id = fields.Many2one('product.product', string="Products", check_company=True)
    product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', string="UOM Category")
    product_qty = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure', )
    price_unit = fields.Float(string='Unit Price', default=0.0, digits='Product Price')
    taxes_id = fields.Many2many('account.tax', string='Taxes', compute='_compute_tax_id', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_all_amount', string='Subtotal')
    advance_subtotal = fields.Monetary(string='Adv. Subtotal', store=True)
    
    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            #fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_id.partner_id.id)
            # filter taxes by company
            taxes = line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == line.env.company)
            #line.taxes_id = fpos.map_tax(taxes, line.product_id, line.custom_entry_id.partner_id)
            line.taxes_id = taxes.ids
            
    @api.depends('product_qty', 'price_unit')
    def _compute_all_amount(self):
        tot = 0
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit
            #self.update({
             #   'price_subtotal': 100
            #})
        
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.taxes_id = self.product_id.supplier_taxes_id.ids
        
            
    #has travel
    t_travel_category = fields.Selection([
        ('domestic', 'Domestic'),
        ('international', 'International'),
        ], string='Travel Category', default='domestic')
    travel_from = fields.Char(string='From')
    travel_to = fields.Char(string='To')
    date_departure = fields.Date(string='Departure Date', )
    date_arrival = fields.Date(string='Arrival Date', )    
    number_of_days = fields.Float(string="Number of Days" , compute = '_number_of_days')
    travel_reference = fields.Many2one('travel.request' , string="Travel Reference")
    t_unit_price = fields.Float(string="Travel Unit Price")
    t_extra_charges = fields.Float(string="Travel Extra Charges")
    t_amount_travel = fields.Float(string="Travel Total Amount", compute='_compute_all_amount_travel')
    
    @api.depends('number_of_days', 't_unit_price', 't_extra_charges')
    def _compute_all_amount_travel(self):
        total_amount_travel = 0
        for line in self:
            total_amount_travel = (line.number_of_days * line.t_unit_price) + line.t_extra_charges
            line.update({
                't_amount_travel': total_amount_travel
            })
    
    @api.onchange('date_departure','date_arrival')
    def _number_of_days(self):
        for line in self:
            if line.date_departure and line.date_arrival:
                if line.date_departure > line.date_arrival:
                    raise UserError(("Arrival Date cant be before Departure Date."))
                else:
                    delta = line.date_arrival - line.date_departure
                    if abs(delta.days) > 0:
                        line.number_of_days = abs(delta.days)
                    else:
                        line.number_of_days = 1
            else:
                line.number_of_days = 0
                
    #has fleet/rent vehicle
    f_fleet_id = fields.Many2one('fleet.vehicle', string="Car Detail")
    f_driver_id = fields.Many2one('res.partner', string="Driver", ondelete='cascade')
    f_job_scope = fields.Selection(
        [('car rental', 'Car Rental.'),
         ('driver ot', 'Driver OT.'),
         ('driver salary', 'Driver Salary.'),
         ('maintenance fee', 'Maintenance Fee.'),
         ('management fee', 'Management Fee.'),
         ('on demand', 'On Demand.'),
         ('petrol charges', 'Petrol Charges.'),
         ('toll fee', 'Toll Fee.'),
         ('replacement', 'Replacement.')],
        string='Job Scope', )
    f_rent_days = fields.Float(string='Days')
    f_amount = fields.Float(string="Amount")
    
    
    #has hotel/accomodation
    h_category = fields.Selection([
        ('travel', 'Travel'),
        ('housing allowance', 'Housing Allowance'),
        ], string='Accomodation Category', default='travel')
    hotel_detail = fields.Char(string="Hotel Detail")
    h_check_in = fields.Date(string="Check-In")
    h_check_out = fields.Date(string="Check-Out")
    h_number_of_nights = fields.Float(string="Number of Nights", compute='_number_of_nights')
    h_travel_id = fields.Many2one('travel.request' , string="Travel Request")
    h_unit_price = fields.Float(string="Hotel Unit Price")
    h_extra_charges = fields.Float(string="Hote Extra Charges")
    h_amount = fields.Float(string="Total Amount", compute='_compute_all_amount_hotel')
    
    @api.depends('h_number_of_nights', 'h_unit_price', 'h_extra_charges')
    def _compute_all_amount_hotel(self):
        total_amount = 0
        for line in self:
            total_amount = (line.h_number_of_nights * line.h_unit_price) + line.h_extra_charges
            line.update({
                'h_amount': total_amount
            })
            
    @api.onchange('h_check_in','h_check_out')
    def _number_of_nights(self):
        for line in self:
            if line.h_check_in and line.h_check_out:
                if line.h_check_in > line.h_check_out:
                    raise UserError(("Check Out cant be before Check in."))
                else:
                    delta = line.h_check_out - line.h_check_in
                    if abs(delta.days) > 0:
                        line.h_number_of_nights = abs(delta.days)
                    else:
                        line.h_number_of_nights = 1
            else:
                line.h_number_of_nights = 0

    #has electricity
    e_paid_to = fields.Selection([
        ('govt', 'Government'),
        ('private', 'Private')],
        string='Paid To')
    date_bill_from = fields.Date(string='Date From', )
    date_bill_to = fields.Date(string='Date To', )
    amount_advanced = fields.Float(string='Forecast', help='Advanced Amount')
    meter_number = fields.Char(string='Meter')
    opening_reading = fields.Integer(string='Opening Reading', help='Opening reading of meter')
    closing_reading = fields.Integer(string='Closing Reading', help='Closing Reading of meter')
    total_unit = fields.Integer(string='Total Unit', compute='_compute_total_units')
    additional_unit = fields.Integer(string='Additional Units')
    maintainence_fee = fields.Float(string='Mnt. Fees', help='Maintenance Fees')
    hp_fee = fields.Float(string='HP Fee', help='Horsepower Fees')
    KHW_charges = fields.Float(string='KHW')
    actual_KHW_charges = fields.Float(string='Actual KHW')
    other_charges = fields.Float(string='Other Charges')
    amount_total_electricity = fields.Float(string='Total', compute='_compute_total_electricity_amount')
    
    #has fuel Drawn
    d_date = fields.Date(string='Drawn Date')
    d_partner_id = fields.Many2one('res.partner',string='Drawn Purchase From', ondelete='cascade')
    d_contact_id = fields.Many2one('res.partner',string='Drawn Contact From', ondelete='cascade')
    d_product_qty = fields.Float(string='Drawn Qty', default=1.0, digits='Product Unit of Measure', )
    d_price_unit = fields.Float(string='Drawn Unit Price', default=1.0, digits='Product Price')
    d_price_subtotal = fields.Monetary(compute='_compute_fuel_drawn_total', string='Drawn Subtotal')
    d_booklet_no = fields.Char(string='Booklet')
    d_receipt_no = fields.Char(string='Receipt No.')
    
    #fuel drawn methods
    @api.depends('d_product_qty', 'd_price_unit')
    def _compute_fuel_drawn_total(self):
        tot = 0
        for line in self:
            if line.custom_entry_id.has_fuel_drawn:
                tot = line.d_product_qty * line.d_price_unit
        self.d_price_subtotal = tot
        
    #Fuel Filling
    f_date = fields.Date(string='Filling Date')
    f_partner_id = fields.Many2one('res.partner',string='Filling Purchase From', ondelete='cascade')
    f_contact_id = fields.Many2one('res.partner',string='Filling Contact From', ondelete='cascade')
    f_gen_name = fields.Char(string='Generator Name')
    f_gen_capacity = fields.Integer(string='Generator Capacity')
    f_curr_drgh = fields.Float(string='Current DRGH')
    f_opening_stock = fields.Float(string='Opening Stock')
    f_closing_stock = fields.Float(string='Closting Stock', compute='_compute_fuel_filled_closing_stock')
    f_product_qty = fields.Float(string='Filling Qty', default=1.0, digits='Product Unit of Measure', )
    f_price_unit = fields.Float(string='Filling Unit Price', default=1.0, digits='Product Price')
    f_price_subtotal = fields.Monetary(compute='_compute_fuel_filled_total', string='Filling Subtotal', store=True)
    f_booklet_no = fields.Char(string='Filling Booklet')
    f_receipt_no = fields.Char(string='Filling Receipt No.')
    
    #fuel filling methods
    @api.depends('f_opening_stock', 'f_product_qty')
    def _compute_fuel_filled_closing_stock(self):
        tot = 0
        for line in self:
            if line.custom_entry_id.has_fuel_filling:
                tot = line.f_opening_stock + line.f_product_qty
        self.update({
            'f_closing_stock': tot
        })
        
    @api.depends('f_product_qty', 'f_price_unit')
    def _compute_fuel_filled_total(self):
        tot = 0
        for line in self:
            tot = 0
            if line.custom_entry_id.has_fuel_filling:
                tot = line.f_product_qty * line.f_price_unit
        self.update({
            'f_price_subtotal': tot
        })
        
    def _compute_state(self):
        for line in self:
            line.state_id = line.project_id.address_id.state_id.id
            
    def _compute_total_units(self):
        for rec in self:
            rec.total_unit = rec.closing_reading - rec.opening_reading

    @api.depends('maintainence_fee','hp_fee','KHW_charges','other_charges')
    def _compute_total_electricity_amount(self):
        for rec in self:
            rec.amount_total_electricity = rec.maintainence_fee + rec.hp_fee + rec.KHW_charges + rec.other_charges
    
    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        taxes_id = self.product_id.supplier_taxes_id
        res = {
            'name': '%s: ' % (self.custom_entry_id.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.product_qty,
            'price_unit': self.price_unit,
            #'tax_ids': [(6, 0, self.taxes_id.ids)],
            #'tax_ids': [(6, 0, taxes_id.ids)],
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'custom_entry_line_id': self.id,
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