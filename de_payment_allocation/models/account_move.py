# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings


class AccountMove(models.Model):
    _inherit = 'account.move'
    
        
    
    def allocate_invoice_payment(self):
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
        
        payments = self.env['account.payment'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('is_reconciled','=', False)])     
        for  payment in  payments:
            payment_amount = 0.0
            currency = 0
            if payment.currency_id.id == self.currency_id.id:
                payment_amount = payment.amount - payment.reconcile_amount
                currency = self.currency_id.id
            else:
                process_amount = payment.amount - payment.reconcile_amount
                payment_amount = payment.currency_id._convert(process_amount, self.currency_id, self.company_id, self.date)
                currency = self.currency_id.id
                
            payment_list.append((0,0,{
                    'payment_id': payment.id,
                    'payment_date': payment.date,
                    'payment_amount': payment.amount,
                    'unallocate_amount': payment_amount,
                    'allocate': False,
                    'allocate_amount': payment_amount,
                    'original_currency_id': payment.currency_id.id,
                    'currency_id': currency,                
            }))
            
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['account.move'].browse(selected_ids)
            
            for  inv in selected_records:
                if inv.state == 'draft':
                    raise UserError(_('Only Posted Invoice are allow to Reconcile!'))
                invoice_list.append((0,0,{
                    'move_id': inv.id,
                    'payment_date': inv.invoice_date,
                    'due_date': inv.invoice_date_due,
                    'invoice_amount': inv.amount_total,
                    'unallocate_amount': inv.amount_residual,
                    'allocate': True,
                    'allocate_amount': inv.amount_residual,
                    'original_currency_id': inv.currency_id.id,
                    'currency_id': inv.currency_id.id,
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
                        'default_invoice_line_ids': invoice_list, 
                        'default_company_id': self.env.company.id,
                        'default_is_invoice': True,
                        'default_partner_id': self.partner_id.id,
                        'default_move_id': self.id,
                       },
        }