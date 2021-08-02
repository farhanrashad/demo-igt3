# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    amount_gst_tax_signed = fields.Monetary(string='Ctax', store=True, readonly=True, compute='_compute_tax_amount', currency_field='company_currency_id')
    amount_wht_tax_signed = fields.Monetary(string='WHT', store=True, readonly=True, compute='_compute_tax_amount', currency_field='company_currency_id')
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_tax_amount(self):
        for move in self:
            total_gst = 0.0
            total_wht = 0.0
            
            total_gst_currency = 0.0
            total_wht_currency = 0.0
            
            for line in move.line_ids:
                if line.tax_line_id:
                    if line.tax_line_id.tax_category == 'gst':
                        total_gst += line.balance
                        total_gst_currency += line.amount_currency
                    elif line.tax_line_id.tax_category == 'wht':
                        total_wht += line.balance
                        total_wht_currency += line.amount_currency
                        
            move.amount_gst_tax_signed = total_gst_currency
            move.amount_wht_tax_signed = total_wht_currency
