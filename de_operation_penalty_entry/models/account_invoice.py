# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date



class AccountMove(models.Model):
    _inherit = 'account.move'

    penalty_entry_id = fields.Many2one('account.penalty.entry', 'Penalty Entry', ondelete='set null', index=True)
    
    @api.onchange('penalty_entry_id')
    def _onchange_penalty_entry_id(self):
        if not self.penalty_entry_id:
            return

        # Copy data from Custom Entry
        invoice_vals = self.penalty_entry_id.with_company(self.penalty_entry_id.company_id)._prepare_invoice()
        #del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy purchase lines.
        penalty_entry_lines = self.penalty_entry_id.custom_entry_line - self.line_ids.mapped('penalty_entry_line_id')
        new_lines = self.env['account.move.line']
        for line in penalty_entry_lines:
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    penalty_entry_line_id = fields.Many2one('account.penalty.entry.line', 'Penalty Entry Line', ondelete='set null', index=True)
    penalty_entry_id = fields.Many2one('account.penalty.entry', 'Penalty Entry', related='penalty_entry_line_id.penalty_entry_id', readonly=True)