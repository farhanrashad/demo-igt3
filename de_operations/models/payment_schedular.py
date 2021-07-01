# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date


class PurchaseSubscription(models.Model):
    _inherit = 'purchase.subscription'
    
    payment_schedule_lines = fields.One2many('purchase.payment.schedular.line', 'subscription_id', string="Payment Schedule")
    journal_id  = fields.Many2one('account.journal', string="Journal")
    account_id  = fields.Many2one('account.account', string="Account")
    
    def action_create_bill(self):
        for payment in self.payment_schedule_lines: 
            if payment.status == 'unpaid':
                if payment.is_bill == True:
                    invoice_line = []
                    invoice_line.append((0,0, {
                                'name': self.code +' '+ self.name,
                                'account_id': self.account_id.id,
                                'quantity': 1, 
                                'purchase_subscription_id': self.id,
                                'price_unit': payment.total_amount,
                                'partner_id': self.partner_id.id,
                                    }))

                    vals = {
                            'partner_id': self.partner_id.id,
                            'journal_id': self.journal_id.id,
                            'invoice_date': fields.Date.today(),
                            'move_type': 'in_invoice',
                            'purchase_subscription_id': self.id,
                            'invoice_origin': self.code,
                            'invoice_line_ids': invoice_line   
                            }
                    move = self.env['account.move'].create(vals)
                    payment.update({
                        'status': 'paid',
                    })

    
    

    @api.onchange('subscription_plan_id') 
    def onchange_subscription_plan(self):
        payment_schedule_ids = []
        for payment_schedule in self.subscription_plan_id.payment_schedule_ids:
            payment_schedule_ids.append((0,0,{
                'date_from': payment_schedule.date_from,
                'date_to': payment_schedule.date_to,
                'no_of_month': payment_schedule.no_of_month,
                'note': payment_schedule.note,
                'monthly_amount': payment_schedule.monthly_amount,
                'total_amount':  payment_schedule.total_amount,
            })) 
        self.payment_schedule_lines = payment_schedule_ids
        
        
class PurchasePaymentSchedularLine(models.Model):
    _name = 'purchase.payment.schedular.line'
    _description = 'Payment Schedule'
    
    is_bill = fields.Boolean(string="Is Bill")
    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    no_of_month = fields.Integer(string="Number of Months", compute="_compute_month")
    note = fields.Char(string="Comments")
    status = fields.Selection(selection=[
            ('unpaid', 'Un-Paid'),
            ('paid', 'Paid'),
        ], string='Invoice', required=True, readonly=True, copy=False, tracking=True,
        default='unpaid')
    monthly_amount = fields.Float(string="Monthly Amount")
    total_amount = fields.Float(string="Monthly Amount", compute="_compute_total")
    subscription_id = fields.Many2one('purchase.subscription',  string="Subscription")

    
    @api.depends('no_of_month', 'monthly_amount')
    def _compute_total(self):
        for payment in self:
            payment.update({
                'total_amount' : payment.no_of_month * payment.monthly_amount 
                })
                
                
    @api.depends('date_from', 'date_to')
    def _compute_month(self):
        for payment in self:
            num_months = 0
            if payment.date_from and payment.date_to:
                num_months = (payment.date_to.year - payment.date_from.year) * 12 + (payment.date_to.month - payment.date_from.month)
    
            payment.update({
                'no_of_month' : num_months
            })                        
       


class PurchaseAgreementPlan(models.Model):
    _inherit = 'purchase.subscription.plan'

    payment_schedule_ids = fields.One2many('payment.schedular.line', 'subscription_plan_id', string="Payment Schedule")
    
        

class PaymentSchedularLine(models.Model):
    _name = 'payment.schedular.line'
    _description = 'Payment Schedule'
    
    
    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    no_of_month = fields.Integer(string="Number of Months", compute="_compute_month")
    note = fields.Char(string="Comments")
    monthly_amount = fields.Float(string="Monthly Amount")
    total_amount = fields.Float(string="Monthly Amount", compute="_compute_total")
    subscription_plan_id = fields.Many2one('purchase.subscription.plan',  string="Subscription Plan")

    
    @api.depends('no_of_month', 'monthly_amount')
    def _compute_total(self):
        for payment in self:
            payment.update({
                'total_amount' : payment.no_of_month * payment.monthly_amount 
                })
                
                
    @api.depends('date_from', 'date_to')
    def _compute_month(self):
        for payment in self:
            num_months = 0
            if payment.date_from and payment.date_to:
                num_months = (payment.date_to.year - payment.date_from.year) * 12 + (payment.date_to.month - payment.date_from.month)
    
            payment.update({
                'no_of_month' : num_months
                })            