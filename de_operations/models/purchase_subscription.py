# -*- coding: utf-8 -*-

from datetime import datetime, time
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class PurchaseSubscriptionType(models.Model):
    _inherit = 'purchase.subscription.type'
    
    deduction_label_types = fields.Char(string='Use Types as', default='Deductions', help="Label used for the deductions of the types.", translate=True)
    move_type = fields.Selection([
        ('in_invoice', 'Bill'),
        ('in_refund', 'Credit Memo')
    ], string='Invoice Type', default='in_refund', required=True)
    journal_id = fields.Many2one('account.journal', string="Accounting Journal",
                                 domain="[('type', '=', 'purchase')]", company_dependent=True,
                                 check_company=True,)
    
    def create_deduction_invoice(self):
        self.ensure_one()
        # If category uses sequence, set next sequence as name
        # (if not, set category name as default name).
        if self.automated_sequence:
            name = self.sequence_id.next_by_id()
        else:
            name = self.name
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_subscription_type_id': self.id,
                'default_user_id': self.env.user.id,
                'default_journal_id': self.journal_id.id,
                'default_move_type': self.move_type,
            },
        }

class PurchaseSubscriptionPlan(models.Model):
    _inherit = 'purchase.subscription.plan'
    
    purchase_subscription_plan_limit_ids = fields.One2many('purchase.subscription.plan.limit', 'subscription_plan_id', string='Limit Lines', copy=True)
    subscription_plan_schedule_ids = fields.One2many('purchase.subscription.plan.schedule', 'subscription_plan_id', string='Payment Schedules', copy=True)
    
    invoicing_mode = fields.Selection(selection_add=[('scheduled', 'Manually with Payment Schedule')], ondelete={'scheduled': 'set default'})
    
    @api.constrains('subscription_plan_schedule_ids','recurring_interval_count')
    def _check_intervals_payment_schedules(self):
        tot = 0
        for schedule in self.subscription_plan_schedule_ids:
            tot += schedule.recurring_interval
        if self.recurring_interval_count != tot:
            raise ValidationError(_("Schedule intervals %s must be equal to total intervals %s",tot,self.recurring_interval_count))

class PurchaseSubscriptionPlanLimit(models.Model):
    _name = 'purchase.subscription.plan.limit'
    _description = 'Subscription Plan Limit'
    
    subscription_plan_id = fields.Many2one('purchase.subscription.plan', string='Subscription Plan', ondelete='cascade')
    state_id = fields.Many2one('res.country.state', required=True)
    min_invoice_amount = fields.Float(string='Minimum Amount', required=True)
    max_invoice_amount = fields.Float(string='Maximum Amount', required=True)
    
class PurchaseSubscriptionPlanSchedule(models.Model):
    _name = 'purchase.subscription.plan.schedule'
    _description = 'Purchase Subscription Plan Schedule'
    
    subscription_plan_id = fields.Many2one('purchase.subscription.plan', string='Subscription Plan',)
    name = fields.Char(string='Name', compute='_compute_name', store=True,)
    recurring_interval = fields.Integer('Intervals', required=True)
    
    
    
    @api.depends('subscription_plan_id.name','subscription_plan_id.recurring_interval_type')
    def _compute_name(self):
        for schedule in self:
            schedule.name = schedule.subscription_plan_id.name + ' - payment schedule for ' + str(schedule.recurring_interval) + ' ' + schedule.subscription_plan_id.recurring_interval_type

    
class PurchaseSubscription(models.Model):
    _inherit = 'purchase.subscription'
    
    invoicing_mode = fields.Selection(related='subscription_plan_id.invoicing_mode')

        
    def generate_recurring_invoice(self):
        plan_limit = False
        for subline in self.purchase_subscription_line:
            plan_limit = self.env['purchase.subscription.plan.limit'].search([('subscription_plan_id','=',self.subscription_plan_id.id),('state_id','=',subline.state_id.id)],limit=1)
            if not (subline.price_subtotal <= plan_limit.max_invoice_amount) or not (subline.price_subtotal >= plan_limit.min_invoice_amount):
                raise UserError(_("Recurring amount must be between '%s' to '%s'", plan_limit.min_invoice_amount,plan_limit.max_invoice_amount))
        res = self._recurring_create_invoice()
        return self.action_subscription_invoice()

    purchase_subscription_schedule_line = fields.One2many('purchase.subscription.schedule', 'purchase_subscription_id', string='Subscription Schedules', copy=True)

    
    def start_subscription(self):
        self.ensure_one()
        next_stage_in_progress = self.env['purchase.subscription.stage'].search([('stage_category', '=', 'progress'), ('sequence', '>=', self.stage_id.sequence)], limit=1)
        if not next_stage_in_progress:
            next_stage_in_progress = self.env['purchase.subscription.stage'].search([('stage_category', '=', 'progress')], limit=1)
        self.stage_id = next_stage_in_progress
        
        if self.subscription_invoice_count == 0:
            if self.purchase_subscription_schedule_line:
                self.purchase_subscription_schedule_line.unlink()
            current_date = self.recurring_next_date or self.default_get(['recurring_next_date'])['recurring_next_date']
            for schedule in self.subscription_plan_id.subscription_plan_schedule_ids:
                new_date = self._get_recurring_next_date(self.recurring_interval_type, self.recurring_interval * schedule.recurring_interval, current_date, self.recurring_invoice_day)
                
                self.purchase_subscription_schedule_line.create({
                    'date_from': current_date,
                    'date_to': new_date,
                    'purchase_subscription_id': self.id,
                    'recurring_intervals': schedule.recurring_interval,
                    'recurring_price': self.recurring_price,
                })
                current_date = self._get_recurring_next_date(self.recurring_interval_type, self.recurring_interval * 1, new_date, self.recurring_invoice_day)
        return True
    
    
class PurchaseSubscriptionLine(models.Model):
    _inherit = 'purchase.subscription.line'
    
    project_id = fields.Many2one('project.project', string='Project')
    state_id = fields.Many2one('res.country.state', related='project_id.address_id.state_id')
    

class PurchaseSubscriptionSchedule(models.Model):
    _name = 'purchase.subscription.schedule'
    _description = 'Purchase Subscription Schedule'
    
    purchase_subscription_id = fields.Many2one('purchase.subscription', string='Subscription', ondelete='cascade')
    
    
    date_from = fields.Date(string='Date From', readonly=True)
    date_to = fields.Date(string='Date To', readonly=True)
    recurring_price = fields.Float(string="Recurring Price", required=True, readonly=True)
    recurring_intervals = fields.Integer(string="Intervals", required=True, readonly=True)
    recurring_sub_total = fields.Float(string="Subtotal", compute='_compute_recurring_all')
    
    discount = fields.Float(string='Discount (%)', digits='Discount')
    escalation = fields.Float(string='Escalation (%)', digits='Discount')
    
    recurring_total = fields.Float(string="Total", compute='_compute_recurring_all')

    invoice_id = fields.Many2one('account.move', string="Invoice", check_company=True)
    company_id = fields.Many2one('res.company', related='purchase_subscription_id.company_id', store=True, index=True)


    @api.depends('recurring_price','recurring_intervals','discount','escalation')
    def _compute_recurring_all(self):
        discount = escalation = 0
        for line in self:
            if line.discount > 0 and line.discount <= 100:
                discount = (line.recurring_price * line.discount) / 100
            if line.escalation > 0 and line.escalation <= 100:
                escalation = (line.recurring_price * line.escalation) / 100
            line.recurring_sub_total = line.recurring_price * line.recurring_intervals
            line.recurring_total = (line.recurring_price - discount + escalation) * line.recurring_intervals
    
    def create_invoice(self):
        res = self._create_invoice()
    
    def _create_invoice(self):
        invoice = self.env['account.move']
        lines_data = []
        for line in self.purchase_subscription_id.purchase_subscription_line:
            lines_data.append([0,0,{
                'name': line.name,
                'purchase_subscription_id': line.purchase_subscription_id.id,
                'price_unit': self.recurring_total or 0.0,
                #'discount': line.discount,
                'quantity': 1,
                'product_uom_id': line.uom_id.id,
                'product_id': line.product_id.id,
                #'tax_ids': [(6, 0, tax_ids.ids)],
                'analytic_account_id': line.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'subscription_start_date': self.date_from,
                'subscription_end_date': self.date_to,
            }])
        invoice_id = invoice.create({
            'move_type': 'in_invoice',
            'purchase_subscription_id': self.purchase_subscription_id.id,
            'invoice_date': fields.Date.today(),
            'partner_id': self.purchase_subscription_id.partner_id.id,
            'partner_shipping_id': self.purchase_subscription_id.partner_id.id,
            'currency_id': self.purchase_subscription_id.currency_id.id,
            'journal_id': self.purchase_subscription_id.subscription_plan_id.journal_id.id,
            'invoice_origin': self.purchase_subscription_id.code,
            #'fiscal_position_id': fpos.id,
            'invoice_payment_term_id': self.purchase_subscription_id.payment_term_id.id,
            'narration': 'test entry',
            'invoice_user_id': self.purchase_subscription_id.user_id.id,
            #'partner_bank_id': company.partner_id.bank_ids.filtered(lambda b: not b.company_id or b.company_id == company)[:1].id,
            'invoice_line_ids':lines_data,
        })
        self.update({
            'invoice_id': invoice_id.id
        })