# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class PurchaseSubscriptionPlan(models.Model):
    _inherit = 'purchase.subscription.plan'
    
    allow_payment_schedule = fields.Boolean(string='Plan Payment Schedule')
    subscription_plan_schedule_ids = fields.One2many('purchase.subscription.plan.schedule', 'subscription_plan_id', string='Payment Schedules', copy=True)
    
    @api.constrains('subscription_plan_schedule_ids','recurring_interval_count')
    def _check_intervals_payment_schedules(self):
        tot = 0
        for schedule in self.subscription_plan_schedule_ids:
            tot += schedule.recurring_interval
        if self.recurring_interval_count != tot:
            raise ValidationError(_("Schedule intervals %s must be equal to total intervals %s",tot,self.recurring_interval_count))


class PurchaseSubscriptionPlanSchedule(models.Model):
    _name = 'purchase.subscription.plan.schedule'
    _description = 'Purchase Subscription Plan Schedule'
    
    subscription_plan_id = fields.Many2one('purchase.subscription.plan', string='Subscription Plan',)
    name = fields.Char(string='Name', compute='_compute_name', store=True,)
    recurring_interval = fields.Integer('Intervals', required=True)
    
class PurchaseSubscription(models.Model):
    _inherit = 'purchase.subscription'    
    
    purchase_subscription_schedule_line = fields.One2many('purchase.subscription.schedule', 'purchase_subscription_id', string='Subscription Schedules', copy=True)
    allow_payment_schedule = fields.Boolean(related='subscription_plan_id.allow_payment_schedule')
    select_all = fields.Boolean(string='Select All', default=False)
    
    @api.onchange('select_all')
    def _select_all(self):
        for line in self.purchase_subscription_schedule_line:
            if not line.invoice_id:
                line.record_selection = self.select_all
    
    def add_record(self):
        lines_data = {}
        for line in self.purchase_subscription_schedule_line:
            date_from = line.date_from
            date_to = line.date_to
            accum = line.accum_escalation
        
        date_from = date_to + relativedelta(days=1)
        date_to = date_from + relativedelta(months=12,days=-1)
            
        subscription_schedule_id = self.env['purchase.subscription.schedule']
        for sub in self:
            lines_data = ({
                'purchase_subscription_id': self.id,
                'date_from': date_from,
                'date_to': date_to,
                'recurring_price': self.recurring_price,
                'recurring_intervals': 12,
                'discount': 0,
                'escalation':  0,
                'accum_escalation': accum,
            })
            #self.env['purchase.subscription.schedule'].create(lines_data)
            subscription_schedule_id.create(lines_data)
            #sub.purchase_subscription_schedule_line(lines_data)
    
    def create_bill(self):
        product_id = False
        for line in self.purchase_subscription_line:
            product_id = line.product_id  
        invoice = self.env['account.move']
        lines_data = []
        if self.purchase_subscription_schedule_line:
            for line in self.purchase_subscription_schedule_line:
                if line.record_selection:
                    lines_data.append([0,0,{
                        'name': str(self.name) + ' ' + str(product_id.name),
                        'purchase_subscription_id': self.id,
                        'purchase_subscription_schedule_id': line.id,
                        'price_unit': line.recurring_price or 0.0,
                        #'discount': line.discount,
                        'quantity': 1,
                        'product_uom_id': product_id.uom_id.id,
                        'product_id': product_id.id,
                        'tax_ids': [(6, 0, product_id.supplier_taxes_id.ids)],
                        #'analytic_account_id': line.analytic_account_id.id,
                        #'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                        #'project_id': line.project_id.id,
                    }])
            invoice.create({
                'move_type': 'in_invoice',
                'purchase_subscription_id': self.id,
                'invoice_date': fields.Datetime.now(),
                'partner_id': self.partner_id.id,
                #'partner_shipping_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'journal_id': self.subscription_plan_id.journal_id.id,
                'invoice_origin': self.name,
                #'fiscal_position_id': fpos.id,
                'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
                'narration': self.name,
                'invoice_user_id': self.user_id.id,
                #'partner_bank_id': company.partner_id.bank_ids.filtered(lambda b: not b.company_id or b.company_id == company)[:1].id,
                'invoice_line_ids':lines_data,
            })
            return invoice
    
class PurchaseSubscriptionSchedule(models.Model):
    _name = 'purchase.subscription.schedule'
    _description = 'Purchase Subscription Schedule'
    
    purchase_subscription_id = fields.Many2one('purchase.subscription', string='Subscription', ondelete='cascade')
    
    record_selection = fields.Boolean(string='Selection', default=False)

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    recurring_price = fields.Float(string="Recurring Price", )
    recurring_intervals = fields.Integer(string="Intervals", )
    recurring_sub_total = fields.Float(string="Subtotal", compute='_compute_recurring_total_all')
    
    discount = fields.Float(string='Discount (%)', digits='Discount')
    escalation = fields.Float(string='Escalation (%)', digits='Discount')
    accum_escalation = fields.Float(string='Accum. Escalation (%)', digits='Discount')
    
    recurring_total = fields.Float(string="Total", compute='_compute_recurring_total_all')
    
    invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True, compute='_get_invoice')
    invoice_status = fields.Selection(related='invoice_id.state')
    company_id = fields.Many2one('res.company', related='purchase_subscription_id.company_id', store=True, index=True)
    
    @api.onchange('escalation')
    def _onchange_escalation(self):
        for line in self:
            line.accum_escalation = line.escalation
    
    def _get_invoice(self):
        for line in self:
            line.invoice_id = self.env['account.move.line'].search([('purchase_subscription_schedule_id','=',line.id)]).move_id.id
            
    def _compute_recurring_total_all(self):
        for line in self:
            line.recurring_sub_total = line.recurring_price * line.recurring_intervals
            line.recurring_total = line.recurring_sub_total + (line.recurring_sub_total * (line.accum_escalation / 100)) - (line.recurring_sub_total * (line.discount / 100))
