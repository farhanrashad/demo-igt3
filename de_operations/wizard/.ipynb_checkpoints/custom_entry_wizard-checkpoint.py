# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomEntryWizard(models.TransientModel):
    _name = "account.custom.entry.wizard.inv"
    _description = "Custom Entry Wizard"
        
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],)
    amount = fields.Float('Down Payment Amount', digits='Account', default=1.0, help="The percentage of amount to be Billed in advance, taxes excluded.")
    amount_bal = fields.Float('Balance Amount', digits='Account', default=1.0, readonly=True)
    amount_advance = fields.Float('Advance Amount', digits='Account', compute='_compute_advance_amount')
    currency_id = fields.Many2one('res.currency', string='Currency')
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits")
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits")
    
    @api.model
    def default_get(self,  default_fields):
        res = super(CustomEntryWizard, self).default_get(default_fields)
        entry_id = self.env['account.custom.entry'].browse(self._context.get('active_ids',[]))
        
        res.update({
            'amount_bal': entry_id.amount_total,
            'currency_id': entry_id.currency_id.id,
        })
        return res
    
    def create_invoices(self):
        purchase_orders = self.env['account.custom.entry'].browse(self._context.get('active_ids', []))
        
    def _compute_advance_amount(self):
        for wizard in self:
            wizard.amount_advance = wizard.amount_bal * (wizard.amount / 100)
    