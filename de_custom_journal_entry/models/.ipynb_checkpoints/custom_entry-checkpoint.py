# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

import json
from lxml import etree

READONLY_STATES = {
        'confirm': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

class CustomEntry(models.Model):
    _name = 'account.custom.entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Custom Entry'
    
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', copy=False, required=True, index=True, default=lambda s: s.env.company, states=READONLY_STATES)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
                                  default=lambda self: self.env.company.currency_id.id)
    user_id = fields.Many2one('res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True,states=READONLY_STATES,)


    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirmed'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=4, default='draft')
        
    date_entry = fields.Datetime('Entry Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now,)

    custom_entry_type_id = fields.Many2one('account.custom.entry.type', string='Entry Type', index=True, required=True, readonly=True, states={'draft': [('readonly', False)],},)
    
    expense_advance = fields.Boolean(related='custom_entry_type_id.expense_advance')
 
    custom_entry_line = fields.One2many('account.custom.entry.line', 'custom_entry_id', string='Entry Line', copy=True, auto_join=True,states=READONLY_STATES)
    
    #account related fields
    expense_advance = fields.Boolean(related='custom_entry_type_id.expense_advance')
    journal_id = fields.Many2one('account.journal',related='custom_entry_type_id.journal_id')
    
    has_partner = fields.Selection(related="custom_entry_type_id.has_partner")
    has_ref = fields.Selection(related="custom_entry_type_id.has_ref")
    has_purchase_requisition = fields.Selection(related="custom_entry_type_id.has_purchase_requisition")
    has_purchase = fields.Selection(related="custom_entry_type_id.has_purchase")
    has_picking = fields.Selection(related="custom_entry_type_id.has_picking")
    has_invoice = fields.Selection(related="custom_entry_type_id.has_invoice")
    has_purchase_subscription = fields.Selection(related="custom_entry_type_id.has_purchase_subscription")
    
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    ref = fields.Char('Reference', copy=False)
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Requisition", check_company=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase", check_company=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True)
    picking_id = fields.Many2one('stock.picking', string="Picking", check_company=True)
    purchase_subscription_id = fields.Many2one('purchase.subscription', string="Purchase Subscription", check_company=True)
    
    has_project = fields.Selection(related="custom_entry_type_id.has_project")
    has_analytic = fields.Selection(related="custom_entry_type_id.has_analytic")
    has_product = fields.Selection(related="custom_entry_type_id.has_product")
    
    has_rent_vechile = fields.Selection(related="custom_entry_type_id.has_rent_vechile")
    has_travel = fields.Selection(related="custom_entry_type_id.has_travel")
    has_hotel = fields.Selection(related="custom_entry_type_id.has_hotel")
    
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)

    
    @api.depends('custom_entry_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for entry in self:
            invoices = entry.mapped('custom_entry_line.invoice_lines.move_id')
            entry.invoice_ids = invoices
            entry.invoice_count = len(invoices)

   
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    def button_confirm(self):
        self.write({'state': 'confirm'})
        return {}

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'state': 'cancel'})
      
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
        res = self._create_custom_invoice()
        #return self.action_subscription_invoice()
        
    def create_custom_invoice(self):
        res = self._create_custom_invoice()
        #return self.action_subscription_invoice()
    
    def _create_custom_invoice(self):
        invoice = self.env['account.move']
        lines_data = []
        for line in self.custom_entry_line:
            lines_data.append([0,0,{
                'name': self.name + ' ' + line.product_id.name,
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
            'partner_shipping_id': self.partner_id.id,
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
    
    
class CustomEntryLine(models.Model):
    _name = 'account.custom.entry.line'
    _description = 'Custom Entry Line'
    
    custom_entry_id = fields.Many2one('account.custom.entry', string='Custom Entry', required=True, ondelete='cascade', index=True, copy=False)
    note = fields.Char(string='Description')
    state = fields.Selection(related='custom_entry_id.state', readonly=True)
    company_id = fields.Many2one(
        string='Company', related='custom_entry_id.company_id',
        store=True, readonly=True, index=True)
    currency_id = fields.Many2one(related='custom_entry_id.currency_id', store=True, string='Currency', readonly=True)

    invoice_lines = fields.One2many('account.move.line', 'custom_entry_line_id', string="Bill Lines", readonly=True, copy=False)

        
    project_id = fields.Many2one('project.project', string="Projects", check_company=True)
    
    analytic_account_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account', )
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', )
    
    product_id = fields.Many2one('product.product', string="Products", check_company=True)
    product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_qty = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure', )
    price_unit = fields.Float(string='Unit Price', default=1.0, digits='Product Price')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    
    #has travel
    date_departure = fields.Date(string='Departure', )
    date_arrival = fields.Date(string='Arrival', )
    travel_from = fields.Char(string='From')
    travel_to = fields.Char(string='To')
    travel_purpose = fields.Char(string='purpose')
    trave_ref = fields.Char(string='reference')
    
    #has vehicle
    vehicle_no = fields.Char(string='Vehicle No.')
    driver_name = fields.Char(string='Driver')
    rent_days = fields.Float(string='Days')
    
    #has hotel
    date_in = fields.Datetime(string='Check In', )
    date_out = fields.Datetime(string='Check Out', )
    #no_of_nights = fields.Integer(string='No. of Nights')
    hote_travel_purpose = fields.Char(string='purpose')
    hotel_name = fields.Char(string='Hotel')

    
    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        tot = 0
        for line in self:
            if line.custom_entry_id.has_product:
                tot = line.product_qty * line.price_unit
        self.update({
            'price_subtotal': line.product_qty * line.price_unit
        })
        
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
    
    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            'name': '%s: ' % (self.custom_entry_id.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.product_qty,
            'price_unit': self.price_unit,
            #'tax_ids': [(6, 0, self.taxes_id.ids)],
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
    
    

