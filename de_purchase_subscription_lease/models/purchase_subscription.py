# -*- coding: utf-8 -*-

from datetime import datetime, time
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
            line.record_selection = self.select_all
    
    def add_record(self):
        lines_data = {}
        for sub in self.purchase_subscription_schedule_line:
            date_from = sub.date_from
            date_to = sub.date_to
        subscription_schedule_id = self.env['purchase.subscription.schedule']
        lines_date = ({
            'purchase_subscription_id': self.id,
            'date_from': date_from,
            'date_to': date_to,
            'recurring_price': self.recurring_price,
            'recurring_intervals': self.recurring_interval,
            'discount': 0,
            'escalation':  1,
            'accum_escalation': 1,
        })
        subscription_schedule_id.create(lines_data)
    
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

    #invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True)
    #company_id = fields.Many2one('res.company', related='purchase_subscription_id.company_id', store=True, index=True)
    
    def _compute_recurring_total_all(self):
        for line in self:
            line.recurring_sub_total = line.recurring_price * line.recurring_intervals
            line.recurring_total = line.recurring_sub_total + (line.recurring_sub_total * (line.accum_escalation / 100))
