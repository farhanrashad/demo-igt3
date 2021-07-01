# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    
    reconcile_amount = fields.Float(string='Reconcile Amount', compute='_compute_reconcile_amount')
    
    def _compute_reconcile_amount(self):
        for payment in self:
            reconcile_amount = 0.0
            for move_line in payment.move_id.line_ids:
                if move_line.credit == 0.0:
                    for credit_line in move_line.matched_credit_ids:
                        reconcile_amount = reconcile_amount + credit_line.amount
            payment.update({
                'reconcile_amount' : reconcile_amount
            })
            if payment.reconcile_amount == payment.amount:
                payment.update({
                'is_reconciled' : True
                })
                
                          
    
    
    
    
    def action_payment_allocation(self):
        currency_accuracy = self.env['decimal.precision'].search([('name','=','Currency Conversion')], limit=1)
        if not currency_accuracy:
            decimal_vals = {
                'name' : 'Currency Conversion',
                'digits':  10,
            }
            accuracy = self.env['decimal.precision'].create(decimal_vals)
        payment_list = []
        invoice_list = []
        partner = []
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['account.payment'].browse(selected_ids)
            
            
        for  payment in  selected_records:
            if payment.state == 'draft':
                raise UserError(_('Only Posted Payment are allow to Reconcile!'))
            if payment.is_reconciled == True:
                raise UserError(_('This Payment Already Reconciled'))
            else:                
                payment_amount = payment.amount - payment.reconcile_amount
               
                payment_list.append((0,0,{
                    'payment_id': payment.id,
                    'payment_date': payment.date,
                    'payment_amount': payment.amount,
                    'unallocate_amount': payment_amount,
                    'allocate': True,
                    'allocate_amount': payment_amount,
                    'currency_id': payment.currency_id.id,
                    'original_currency_id': payment.currency_id.id,
                }))
                partner.append(payment.partner_id.id)
        uniq_partner =  set(partner) 
        for ppartner in uniq_partner:
            invoices = self.env['account.move'].search([('partner_id','=',ppartner),('state','=','posted'),('payment_state','in', ('not_paid','partial'))])             
            for  inv in invoices:
                amount = 0.0
                currency = 0
                if inv.currency_id.id == self.currency_id.id:
                    amount = inv.amount_residual
                    currency = inv.currency_id.id 
                else:
                    amount = inv.currency_id._convert(inv.amount_residual, self.currency_id, self.company_id, self.date)
                    currency = self.currency_id.id 

                invoice_list.append((0,0,{
                    'move_id': inv.id,
                    'payment_date': inv.invoice_date,
                    'due_date': inv.invoice_date_due,
                    'invoice_amount': inv.amount_total,
                    'unallocate_amount': amount,
                    'allocate': False,
                    'allocate_amount': amount,
                    'currency_id': currency,
                    'original_currency_id': inv.currency_id.id, 
                }))    
        return {
            'name': ('Payment Allocation'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.allocation.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_payment_line_ids': payment_list, 
                        'default_invoice_move_ids': invoice_list, 
                        'default_company_id': self.env.company.id,
                        'default_partner_id': self.partner_id.id,
                        'default_is_payment': True,
                        'default_account_id': self.destination_account_id.id,
                        'default_payment_id': self.id,
                       },
        }

