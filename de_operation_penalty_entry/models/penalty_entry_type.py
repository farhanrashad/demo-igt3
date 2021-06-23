# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource
from random import randint

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]

class PenaltyEntryType(models.Model):
    _name = 'account.penalty.entry.type'
    _description = 'Penalty Entry Type'
    _order = 'id'
    
    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')
    
    label_types = fields.Char(string='Use Types as', default='Penalty Entry', help="Label used for the subscriptions of the types.", translate=True)

    image = fields.Binary(string='Image', )
    color = fields.Integer(string='Color Index')
    company_id = fields.Many2one(
        'res.company', 'Company', copy=False,
        required=True, index=True, default=lambda s: s.env.company)
    automated_sequence = fields.Boolean('Automated Sequence?',
        help="If checked, the Approval Requests will have an automated generated name based on the given code.")
    sequence_code = fields.Char(string="Code")

    sequence_id = fields.Many2one('ir.sequence', 'Reference Purchase Subscription Sequence',
        copy=False, check_company=True)
    
    expense_advance = fields.Boolean(string='Pay Advance Expense')
    journal_id = fields.Many2one('account.journal', string="Accounting Journal", required=True, company_dependent=True, check_company=True,)

    
    #Main Type fields
    has_penalty_fields = fields.Selection(CATEGORY_SELECTION, string="Penalty Alarm & Invoices", default="no", required=True,)
    has_asset_fields = fields.Selection(CATEGORY_SELECTION, string="Asset Lifetime Invoices", default="no", required=True,)
    has_hse_fields = fields.Selection(CATEGORY_SELECTION, string="HSE Invoice", default="no", required=True,)
    has_pm_fields = fields.Selection(CATEGORY_SELECTION, string="PM Invoice", default="no", required=True,)
    has_power_fuel_fields = fields.Selection(CATEGORY_SELECTION, string="Power & Fuel Invoice", default="no", required=True,)
    has_sla_fields = fields.Selection(CATEGORY_SELECTION, string="SLA Invoice", default="no", required=True,)

    #header fields    
    has_partner = fields.Selection(CATEGORY_SELECTION, string="Partner", default="no", required=True,)
    has_invoice = fields.Selection(CATEGORY_SELECTION, string="Invoice", default="no", required=True,)

    


    


    @api.model
    def create(self, vals):
        if vals.get('automated_sequence'):
            sequence = self.env['ir.sequence'].create({
                'name': _('Sequence') + ' ' + vals['sequence_code'],
                'padding': 5,
                'prefix': vals['sequence_code'],
                'company_id': vals.get('company_id'),
            })
            vals['sequence_id'] = sequence.id

        penalty_entry_type = super().create(vals)
        return penalty_entry_type

    def write(self, vals):
        if 'sequence_code' in vals:
            for penalty_entry_type in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if penalty_entry_type.sequence_id:
                    penalty_entry_type.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', penalty_entry_type.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    penalty_entry_type.sequence_id = sequence
        if 'company_id' in vals:
            for penalty_entry_type in self:
                if penalty_entry_type.sequence_id:
                    penalty_entry_type.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)
    
    def create_request(self):
        self.ensure_one()
        if self.automated_sequence:
            name = self.sequence_id.next_by_id()
        else:
            name = self.name
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.penalty.entry",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_name': name,
                'default_penalty_entry_type_id': self.id,
                'default_user_id': self.env.user.id,
            },
        }