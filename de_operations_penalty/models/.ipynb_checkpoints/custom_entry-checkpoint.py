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
    
    def _get_default_stage_id(self):
        return self.env['account.custom.entry.stage'].search([('stage_category','=','draft')], order='sequence', limit=1)
    
    def unlink(self):
        for r in self:
            if r.state != 'draft' or r.state == 'cancel':
                raise UserError(
                    "You can not delete records other than in draft/cancelled state.")
        for rec in self:
            if rec.stage_id.stage_category != 'draft' or rec.stage_id.stage_category != 'cancel':
                raise UserError(
                    "You can not delete records other than in draft/cancelled state.")
        return super(CustomEntry, self).unlink()
    
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', copy=False, required=True, index=True, default=lambda s: s.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, 
                                  default=lambda self: self.env.company.currency_id.id)
    text = fields.Text(string="")
    user_id = fields.Many2one('res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True,)
   

    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirmed'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=4, default='draft')
        
    date_entry = fields.Datetime('Entry Date', required=True, index=True, copy=False, default=fields.Datetime.now,)

    custom_entry_type_id = fields.Many2one('account.custom.entry.type', string='Entry Type', index=True, required=True, readonly=True, states={'draft': [('readonly', False)],},)
    stage_id = fields.Many2one('account.custom.entry.stage', string='Stage', compute='_compute_stage_id', store=True, readonly=False, ondelete='restrict', tracking=True, index=True, default=_get_default_stage_id, copy=False)
    stage_category = fields.Selection(related='stage_id.stage_category')
                                   
    expense_advance = fields.Boolean(related='custom_entry_type_id.expense_advance')
 
    custom_entry_line = fields.One2many('account.custom.entry.line', 'custom_entry_id', string='Entry Line', copy=True, auto_join=True)
    
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
    
    #fleet form
    has_fleet_fields = fields.Selection(related="custom_entry_type_id.has_fleet_fields")
    #fleet form field datatype define
    ref_fleet = fields.Char('Reference', copy=False)
    supplier_inv_no_fleet = fields.Char(string='Supplier Invoice Number')
#     amount_total_fleet = fields.Float(string='Amount Total', compute="_compute_total_fleet")
    duration_from = fields.Date(string='Duration')
    duration_to = fields.Date(string='')
    period_fleet = fields.Date(string='Period')
    taxes_fleet = fields.Many2one('account.tax', string='Taxes')
      
    #travel form
    has_travel_fields = fields.Selection(related="custom_entry_type_id.has_travel_fields")
    #travel form field datatype define
    ref_travel = fields.Char('Reference', copy=False)
    supplier_inv_no_travel = fields.Char(string='Supplier Invoice Number')
    travel_by = fields.Selection(
        [('flight ticket', 'Flight Ticket'),
         ('Vehicle', 'Vehicle Rental')],
        string='Travel By', track_visibility="always")
    customer_type = fields.Selection([('local', 'Local'), ('expat', 'Expat')], string='Customer Type')
#     amount_total_travel = fields.Float(string='Amount Total', compute="_compute_total_travel")
    effective_date = fields.Date(string='Effected Date')
    date_of_sub = fields.Date(string='Date of Subscription')
    taxes_travel = fields.Many2one('account.tax', string='Taxes')
       
    #accommodation form
    has_accommodation_fields = fields.Selection(related="custom_entry_type_id.has_accommodation_fields")
    #accommodation form field datatype define
    ref_accom = fields.Char('Reference', copy=False)
    supplier_inv_no_accom = fields.Char(string='Supplier Invoice Number')
    customer_type_accom = fields.Selection([('local', 'Local'), ('expat', 'Expat')], string='Customer Type')
#     amount_total_accom = fields.Float(string='Amount Total' , compute="_compute_total_accom")
    effective_date_accom = fields.Date(string='Effected Date')
    date_of_sub_accom = fields.Date(string='Date of Subscription')
    period = fields.Date('Period')
    taxes_accom = fields.Many2one('account.tax', string='Taxes')
    
#     partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    partner_id = fields.Many2one('res.users', default=lambda self: self.env.user, String="Supplier")
    amount_total_all = fields.Float(string="Total Amount", compute="_compute_amount_total_all")
    ref = fields.Char('Reference', copy=False)
    invoice_no_fleet = fields.Many2one('account.move', string='Invoice Number', compute="_compute_invoice_no_fleet", readonly=True)
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Requisition", check_company=True)
    purchase_id = fields.Many2one('purchase.order', string="Purchase", check_company=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True)
    picking_id = fields.Many2one('stock.picking', string="Picking", check_company=True)
    purchase_subscription_id = fields.Many2one('purchase.subscription', string="Purchase Subscription", check_company=True)
    
#     has_project = fields.Selection(related="custom_entry_type_id.has_project")
#     has_analytic = fields.Selection(related="custom_entry_type_id.has_analytic")
#     has_product = fields.Selection(related="custom_entry_type_id.has_product")
    
#     has_rent_vechile = fields.Selection(related="custom_entry_type_id.has_rent_vechile")
#     has_travel = fields.Selection(related="custom_entry_type_id.has_travel")
#     has_hotel = fields.Selection(related="custom_entry_type_id.has_hotel")
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    
#     for rec in self:
#         if rec.has_fleet_field == 'required':
#             rec.custom_entry_type_id = rec.account.custom.entry.type
#         else
    

    @api.depends('custom_entry_type_id')
    def _compute_stage_id(self):
        for entry in self:
            if entry.custom_entry_type_id:
                if entry.custom_entry_type_id not in entry.stage_id.custom_entry_type_ids:
                    entry.stage_id = entry.stage_find(order.custom_entry_type_id.id, [('fold', '=', False), ('stage_category', '=', 'draft')])
            else:
                order.stage_id = False
    
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
                               
            
    @api.depends('custom_entry_line.amount','custom_entry_line.amount_accom','custom_entry_line.amount_travel')
    def _compute_amount_total_all(self):
        for record in self:
            amount_total = 0.0
            if record.custom_entry_type_id.has_fleet_fields == 'required':
                for line in record.custom_entry_line:
                    amount_total = line.amount + amount_total
                record.update({
                    'amount_total_all': amount_total,
                })
            elif record.custom_entry_type_id.has_accommodation_fields == 'required':
                for line in record.custom_entry_line:
                    amount_total = line.amount_accom + amount_total
                record.update({
                    'amount_total_all': amount_total,
                })
            elif record.custom_entry_type_id.has_travel_fields == 'required':
                for line in record.custom_entry_line:
                    amount_total = line.amount_travel + amount_total
                record.update({
                    'amount_total_all': amount_total,
                })
            else:
                record.update({
                    'amount_total_all': 0.0,
                })
    
#     @api.depends('custom_entry_line.amount')
#     def _compute_total_fleet(self):
#         for record in self:
#             amount_total = 0.0
#             for line in record.custom_entry_line:
#                 amount_total = line.amount + amount_total
#             record.update({
#                 'amount_total_fleet': amount_total,
#             })
            
#     @api.depends('custom_entry_line.amount_accom')
#     def _compute_total_accom(self):
#         for record in self:
#             amount_total = 0.0
#             for line in record.custom_entry_line:
#                 amount_total = line.amount_accom + amount_total
#             record.update({
#                 'amount_total_accom': amount_total,
#             })
            
#     @api.depends('custom_entry_line.amount_travel')
#     def _compute_total_travel(self):
#         for record in self:
#             amount_total = 0.0
#             for line in record.custom_entry_line:
#                 amount_total = line.amount_travel + amount_total
#             record.update({
#                 'amount_total_travel': amount_total,
#             })
            
            
           
    
    @api.depends('custom_entry_line.invoice_lines.move_id')
    def _compute_invoice(self):
        for entry in self:
            invoices = entry.mapped('custom_entry_line.invoice_lines.move_id')
            entry.invoice_ids = invoices
            entry.invoice_count = len(invoices)
            
            
    def _compute_invoice_no_fleet(self):
        for entry in self:
            related_invoice = self.env['account.move'].search([('invoice_origin','=',entry.name)],limit=1)
            entry.update({
                'invoice_no_fleet' : related_invoice.id,
            })
            
            
   
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    def action_confirm(self):
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        return {}

    def action_refuse(self):
        

        
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['account.custom.entry'].browse(selected_ids)
            return {
            'name': ('Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.entry.refuse.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_custom_entry_id': self.id, 
                       },}
        
        
    def action_submit(self):
        self.ensure_one()
        if not self.custom_entry_line:
            raise UserError(_("You cannot submit requisition '%s' because there is no product line.", self.name))
        self.update({
            'stage_id' : self.stage_id.next_stage_id.id,
        })
        

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
        
        if self.custom_entry_type_id.has_fleet_fields != 'no':
            for line in self.custom_entry_line:
                lines_data.append([0,0,{
                    'name': self.name + ' , ' + line.job_scope + ' , ' + line.car_details.name + ' , ' + str(self.duration_from) + ' - ' + str(self.duration_to),
                    'custom_entry_line_id': line.id,
                    'price_unit': line.amount or 0.0,
                    'quantity': 1.0,
                    'account_id' : line.job_scope_account.id,
                    'tax_ids': [(self.taxes_fleet.id)] if self.taxes_fleet.id else False,
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
            
            
        elif self.custom_entry_type_id.has_travel_fields != 'no':
            for line in self.custom_entry_line:
                lines_data.append([0,0,{
                    'name': self.name + ' - ' + self.travel_by + ' - ' + str(line.user.name) + ' - ' + str(line.fromm) + ' - ' + str(line.to) + ' - ' + str(line.departure_date) + ' - ' + str(line.arrival_date),
                    'custom_entry_line_id': line.id,
                    'price_unit': line.amount_travel or 0.0,
                    #'discount': line.discount,
                    'quantity': 1.0,
                    'account_id' : line.travel_account.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'product_id': line.product_id.id,
                    'tax_ids': [(self.taxes_travel.id)] if self.taxes_travel.id else False,
    #                 'analytic_account_id': line.analytic_account_id.id,
    #                 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
    #                 'project_id': line.project_id.id,
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
            
        elif self.custom_entry_type_id.has_accommodation_fields != 'no':
            for line in self.custom_entry_line:
                lines_data.append([0,0,{
                    'name': self.name + ' - ' + str(line.category_accom) + str(line.check_in) + ' - ' + str(line.check_out) + ' - ' + str(line.user_accom.name),
                    'custom_entry_line_id': line.id,
                    'price_unit': line.amount_accom or 0.0,
                    #'discount': line.discount,
                    'quantity': 1.0,
                    'account_id' : line.accom_account.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'product_id': line.product_id.id,
                    'tax_ids': [(self.taxes_accom.id)] if self.taxes_accom.id else False,
    #                 'analytic_account_id': line.analytic_account_id.id,
    #                 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
    #                 'project_id': line.project_id.id,
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
#     note = fields.Char(string='Description')
    state = fields.Selection(related='custom_entry_id.state', readonly=True)
    company_id = fields.Many2one(
        string='Company', related='custom_entry_id.company_id',
        store=True, readonly=True, index=True)
    currency_id = fields.Many2one(related='custom_entry_id.currency_id', store=True, string='Currency', readonly=True)

    invoice_lines = fields.One2many('account.move.line', 'custom_entry_line_id', string="Bill Lines", readonly=True, copy=False)

    #fleet line-model field data type define
    car_details = fields.Many2one('fleet.vehicle', string="Car Detail")
    driver = fields.Many2one('res.partner', string="Driver")
    user = fields.Many2one('hr.employee',string="User")
    job_scope = fields.Selection(
        [('car rental', 'Car Rental.'),
         ('driver ot', 'Driver OT.'),
         ('driver salary', 'Driver Salary.'),
         ('maintenance fee', 'Maintenance Fee.'),
         ('management fee', 'Management Fee.'),
         ('on demand', 'On Demand.'),
         ('petrol charges', 'Petrol Charges.'),
         ('toll fee', 'Toll Fee.'),
         ('replacement', 'Replacement.')],
        string='Job Scope', track_visibility="always")
    job_scope_account = fields.Many2one('account.account', string= "Account", compute='account_job_scope')
    days = fields.Integer(string="Days")
    amount = fields.Float(string="Amount (MMK)")
    remark = fields.Char(string="Remark")
    
    #travel line-model field data type define
    category = fields.Selection([
        ('domestic', 'Domestic'),
        ('international', 'International'),
        ], string='Category', default='domestic')
    fromm = fields.Char(string="From")
    to = fields.Char(string="To")
    departure_date = fields.Date(string="Departure Date")
    arrival_date = fields.Date(string="Arrival Date")
    number_of_days = fields.Float(string="Number of Days" , compute = '_number_of_days')
    travel_reference = fields.Many2one('travel.request' , string="Travel Reference")
    description = fields.Char(related='travel_reference.description_main',string="Description")
    travel_for = fields.Selection(related='travel_reference.travel_type',string="Travel For")
    unit_price = fields.Float(string="Unit Price")
    extra_charges = fields.Float(string="Extra Charges")
    user_travel = fields.Many2one('res.users',string="User")
    amount_travel = fields.Float(string="Total Amount", compute='_compute_amount_travel')
    remark_travel = fields.Char(string="Remark")
    travel_account = fields.Many2one('account.account', string= "Account", compute='account_travel')
    
    
    @api.onchange('departure_date','arrival_date')
    def _number_of_days(self):
        for line in self:
            if line.departure_date and line.arrival_date:
                if line.departure_date > line.arrival_date:
                    raise UserError(("Arrival Date cant be before Departure Date."))
                else:
                    delta = line.arrival_date - line.departure_date
                    if abs(delta.days) > 0:
                        line.number_of_days = abs(delta.days)
                    else:
                        line.number_of_days = 1
            else:
                line.number_of_days = 0
    
    
    
    @api.onchange('car_details')
    def _get_driver_user(self):
        if self.car_details and self.custom_entry_id.duration_from:
            current_user = self.env['fleet.vehicle.user.log'].search([('vehicle_id','=',self.car_details.id),('date_start','<=',self.custom_entry_id.duration_from),('date_end','>',self.custom_entry_id.duration_from)],limit=1)
            current_driver = self.env['fleet.vehicle.assignation.log'].search([('vehicle_id','=',self.car_details.id),('date_start','<=',self.custom_entry_id.duration_from),('date_end','>',self.custom_entry_id.duration_from)],limit=1)
            if current_user:
                self.update({
                    'user': current_user.user_id.id
                })
            if current_driver:
                self.update({
                    'driver': current_driver.driver_id.id
                })
    
    @api.depends('number_of_days', 'unit_price', 'extra_charges')
    def _compute_amount_travel(self):
        total_amount_travel = 0
        for line in self:
            if line.number_of_days or line.unit_price or line.extra_charges:
                total_amount_travel = (line.number_of_days * line.unit_price) + line.extra_charges
            line.update({
                'amount_travel': total_amount_travel
            })
        
    @api.depends('job_scope')
    def account_job_scope(self):
        for record in self:
            for line in self:
                if line.job_scope == 'car rental':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685200')]).id,
                })
                elif line.job_scope == 'driver ot':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685400')]).id,
                })
                elif line.job_scope == 'driver salary':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685400')]).id,
                })
                elif line.job_scope == 'maintenance fee':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685300')]).id,
                })
                elif line.job_scope == 'management fee':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685400')]).id,
                })
                elif line.job_scope == 'on demand':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685200')]).id,
                })
                elif line.job_scope == 'petrol charges':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685100')]).id,
                })
                elif line.job_scope == 'toll fee':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685500')]).id,
                })
                elif line.job_scope == 'replacement':
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685200')]).id,
                })
                else:
                    line.update({
                    'job_scope_account': self.env['account.account'].search([('code','=', '685300')]).id,
                })
                    
                    
                    
    @api.depends('amount_travel')
    def account_travel(self):
        for record in self:
            if record.custom_entry_id.travel_by == 'flight ticket' and record.custom_entry_id.customer_type == 'local':
                record.update({
                'travel_account': self.env['account.account'].search([('code','=', '670200')]).id,
            })
            elif record.custom_entry_id.travel_by == 'Vehicle' and record.custom_entry_id.customer_type == 'local':
                record.update({
                'travel_account': self.env['account.account'].search([('code','=', '685200')]).id,
            })
            elif record.custom_entry_id.travel_by == 'Vehicle' and record.custom_entry_id.customer_type == 'expat':
                record.update({
                'travel_account': self.env['account.account'].search([('code','=', '685200')]).id,
            })
            elif record.custom_entry_id.travel_by == 'flight ticket' and record.custom_entry_id.customer_type == 'expat':
                record.update({
                'travel_account': self.env['account.account'].search([('code','=', '655210')]).id,
            })
            else:
                record.update({
                'travel_account': self.env['account.account'].search([('code','=', '655210')]).id,
            })
    
    #accommodation line-model field data type define
    category_accom = fields.Selection([
        ('travel', 'Travel'),
        ('housing allowance', 'Housing Allowance'),
        ], string='Category', default='travel')
    user_accom = fields.Many2one('res.users',string="User")
    hotel_detail = fields.Char(string="Hotel Detail")
    check_in = fields.Date(string="Check-In")
    check_out = fields.Date(string="Check-Out")
    number_of_nights = fields.Float(string="Number of Nights", compute='_number_of_nights')
    travel_reference_accom = fields.Many2one('travel.request' , string="Travel Reference")
    description_accom = fields.Char(related='travel_reference_accom.description_main',string="Description")
    travel_for_accom = fields.Selection(related='travel_reference_accom.travel_type',string="Travel For")
    unit_price_accom = fields.Float(string="Unit Price")
    extra_charges_accom = fields.Float(string="Extra Charges")
    remark_accom = fields.Char(string="Remark")
    amount_accom = fields.Float(string="Total Amount", compute='_compute_amount_accom')
    accom_account = fields.Many2one('account.account', string= "Account", compute='account_accom')
    
    @api.depends('number_of_nights', 'unit_price_accom', 'extra_charges_accom')
    def _compute_amount_accom(self):
        total_amount = 0
        for line in self:
            if line.number_of_nights or line.unit_price_accom or line.extra_charges_accom:
                total_amount = (line.number_of_nights * line.unit_price_accom) + line.extra_charges_accom
            line.update({
                'amount_accom': total_amount
            })

    @api.onchange('check_in','check_out')
    def _number_of_nights(self):
        for line in self:
            if line.check_in and line.check_out:
                if line.check_in > line.check_out:
                    raise UserError(("Check Out cant be before Check in."))
                else:
                    delta = line.check_out - line.check_in
                    if abs(delta.days) > 0:
                        line.number_of_nights = abs(delta.days)
                    else:
                        line.number_of_nights = 1
            else:
                line.number_of_nights = 0
        
        
    @api.depends('amount_accom')
    def account_accom(self):
        for record in self:
            if record.category_accom == 'housing allowance' and record.custom_entry_id.customer_type_accom == 'local':
                record.update({
                'accom_account': self.env['account.account'].search([('code','=', '670100')]).id,
            })
            elif record.category_accom == 'travel' and record.custom_entry_id.customer_type_accom == 'local':
                record.update({
                'accom_account': self.env['account.account'].search([('code','=', '670100')]).id,
            })
            elif record.category_accom == 'housing allowance' and record.custom_entry_id.customer_type_accom == 'expat':
                record.update({
                'accom_account': self.env['account.account'].search([('code','=', '670100')]).id,
            })
            elif record.category_accom == 'travel' and record.custom_entry_id.customer_type_accom == 'expat':
                record.update({
                'accom_account': self.env['account.account'].search([('code','=', '670100')]).id,
            })
            else:
                record.update({
                'accom_account': self.env['account.account'].search([('code','=', '670100')]).id,
            })

#     analytic_account_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account', )
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags', )
    
#     product_id = fields.Many2one('product.product', string="Products", check_company=True)
#     product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure",
#         domain="[('category_id', '=', product_uom_category_id)]")
#     product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
#     product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
#     price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
#     price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    
#     #has travel
#     date_departure = fields.Date(string='Departure', )
#     date_arrival = fields.Date(string='Arrival', )
#     travel_from = fields.Char(string='From')
#     travel_to = fields.Char(string='To')
#     travel_purpose = fields.Char(string='purpose')
#     trave_ref = fields.Char(string='reference')
    
#     #has vehicle
#     vehicle_no = fields.Char(string='Vehicle No.')
#     driver_name = fields.Char(string='Driver')
    
#     #has hotel
#     date_in = fields.Datetime(string='Check In', )
#     date_out = fields.Datetime(string='Check Out', )
#     #no_of_nights = fields.Integer(string='No. of Nights')
#     hote_travel_purpose = fields.Char(string='purpose')
#     hotel_name = fields.Char(string='Hotel')

    
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
    
    

