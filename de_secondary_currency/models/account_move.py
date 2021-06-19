# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_base_signed = fields.Monetary(string='Total base.Curr.', readonly=True, compute='_compute_all_currency_conversion_amount', currency_field='company_currency_id')
    
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
    def _compute_all_currency_conversion_amount(self):
        for move in self:
            total_base_signed = 0.0
            if not (move.currency_id.id == move.company_id.currency_id.id):
                total_base_signed += move.currency_id._get_conversion_rate(move.currency_id, move.company_currency_id,move.company_id, move.date) * move.amount_total_signed
            else:
                total_base_signed = move.amount_total_signed
            move.update({
                'total_base_signed': total_base_signed,
            })