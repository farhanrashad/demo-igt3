# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

class PurchaseSubscriptionAdjustments(models.TransientModel):
    _name = 'purchase.subscription.plan.wizard'
    _description = 'Purchase Subscription Plan'
    
    @api.model
    def default_get(self,  default_fields):
        res = super(PurchaseSubscriptionAdjustments, self).default_get(default_fields)
        subscription = self.env['purchase.subscription'].browse(self._context.get('active_ids',[]))
        order = []
        #for subscription in subscriptions:
        #    order.append((0,0,{
        #        'journal_id' : subscription.subscription_plan_id.journal_id.id,
        #    }))
        res.update({
            'purchase_subscription_id': subscription.id,
            })
        return res
    
    amount = fields.Float('Escalation %', digits='Account', help="The percentage of amount to be Billed in advance, taxes excluded.")
    currency_id = fields.Many2one('res.currency', string='Currency')
    purchase_subscription_id = fields.Many2one('purchase.subscription','Vendor Bill',)
    recurring_interval = fields.Integer(string="Invoicing Period", help="Repeat every (Days/Week/Month/Year)", required=True, default=1, tracking=True)
    recurring_interval_type = fields.Selection([('daily', 'Days'), ('weekly', 'Weeks'),
                                                ('monthly', 'Months'), ('yearly', 'Years'), ],
                                               string='Recurrence', required=True,
                                               help="Invoice automatically repeat at specified interval", default='monthly', tracking=True)
    wizard_plan_line_ids = fields.One2many('purchase.subscription.plan.line.wizard', 'wizard_subscription_plan_id',string="Planned Line")


    def populate_subscription(self):
        self.ensure_one()
        current_date = new_date = False
        if self.wizard_plan_line_ids:
            self.wizard_plan_line_ids.unlink()
        #current_date = self.recurring_next_date or self.default_get(['recurring_next_date'])['recurring_next_date']
        for schedule in self.purchase_subscription_id.subscription_plan_id.subscription_plan_schedule_ids:
            #new_date = self.subscription_plan_id._get_recurring_next_date(self.recurring_interval_type, self.recurring_interval * schedule.recurring_interval, current_date, self.recurring_invoice_day)
                
            self.wizard_plan_line_ids.create({
                'date_from': current_date,
                'date_to': new_date,
                'wizard_subscription_plan_id': self.purchase_subscription_id.id,
                'recurring_intervals': schedule.recurring_interval,
                'recurring_price': self.purchase_subscription_id.recurring_price,
            })
                #current_date = self._get_recurring_next_date(self.recurring_interval_type, self.recurring_interval * 1, new_date, self.recurring_invoice_day)
        #return True
    
    def create_invoices(self):
        subscriptions = self.env['purchase.subscription'].browse(self._context.get('active_ids', []))

        if self.invoice_type:
            for order in subscriptions:
                amount, name = self._get_advance_details(order)
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                #tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_id).ids
                analytic_tag_ids = []
                #for line in order.order_line:
                    #analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                moves = self._create_invoice(order, amount)

        if self._context.get('open_bills', False):
            return subscriptions.action_subscription_invoice()
        return {'type': 'ir.actions.act_window_close'}
    
    def _get_advance_details(self, order):
        context = {'lang': order.partner_id.lang}
        if self.adjustment_payment_method == 'percentage':
            amount = order.recurring_total * self.amount / 100
            #name = _("Adjustments of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
        name = self.reason
        del context

        return amount, name
    
    def _create_invoice(self, order, amount):
        if (self.adjustment_payment_method == 'percentage' and self.amount <= 0.00) or (self.adjustment_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_bill_values(order, name, amount,)

        #if order.fiscal_position_id:
            #invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice
    
    def _prepare_bill_values(self, order, name, amount,):
        partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.ref,
            'move_type': self.invoice_type,
            'narration': self.reason,
            'invoice_origin': order.name,
            'purchase_subscription_id': order.id,
            'invoice_user_id': order.user_id.id,
            'partner_id': partner_invoice_id,
            #'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'currency_id': order.currency_id.id,
            'payment_reference': self.ref or '',
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'purchase_subscription_id': order.id,
                #'tax_ids': [(6, 0, po_line.taxes_id.ids)],
                'analytic_tag_ids': [(6, 0, order.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals

class SubscriptionPlanLineWizard(models.TransientModel):
    _name = 'purchase.subscription.plan.line.wizard'
    _description = "Subscription Plan Line Wixard"
    
    wizard_subscription_plan_id = fields.Many2one('purchase.subscription.plan.wizard')
    date_from = fields.Date(string='Date From', readonly=True)
    date_to = fields.Date(string='Date To', readonly=True)
    recurring_price = fields.Float(string="Recurring Price", required=True, readonly=True)
    recurring_intervals = fields.Integer(string="Intervals", required=True, readonly=True)