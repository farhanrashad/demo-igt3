# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_entry_id = fields.Many2one('account.custom.entry', 'Custom Entry', ondelete='set null', index=True)
    
    @api.onchange('custom_entry_id')
    def _onchange_custom_entry_id(self):
        if not self.custom_entry_id:
            return

        # Copy data from Custom Entry
        invoice_vals = self.custom_entry_id.with_company(self.custom_entry_id.company_id)._prepare_invoice()
        #del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy purchase lines.
        custom_entry_lines = self.custom_entry_id.custom_entry_line - self.line_ids.mapped('custom_entry_line_id')
        new_lines = self.env['account.move.line']
        for line in custom_entry_lines:
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    custom_entry_line_id = fields.Many2one('account.custom.entry.line', 'Custom Entry Line', ondelete='set null', index=True)
    custom_entry_id = fields.Many2one('account.custom.entry', 'Custom Entry', related='custom_entry_line_id.custom_entry_id', readonly=True)