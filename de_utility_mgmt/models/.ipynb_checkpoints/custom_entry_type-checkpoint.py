# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource
from random import randint

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]

class CustomEntryType(models.Model):
    _name = 'account.custom.entry.type'
    _description = 'Custom Entry Type'
    _order = 'id'
    
    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')
    
    label_types = fields.Char(string='Use Types as', default='Custom Entry', help="Label used for the subscriptions of the types.", translate=True)

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

        
    #header fields    
    has_partner = fields.Selection(CATEGORY_SELECTION, string="Partner", default="no", required=True,)
    has_ref = fields.Selection(CATEGORY_SELECTION, string="Reference", default="no", required=True,)
    has_purchase_requisition = fields.Selection(CATEGORY_SELECTION, string="Requisition", default="no", required=True,)
    has_purchase = fields.Selection(CATEGORY_SELECTION, string="Purchase", default="no", required=True,)
    has_picking = fields.Selection(CATEGORY_SELECTION, string="Picking", default="no", required=True,)
    has_invoice = fields.Selection(CATEGORY_SELECTION, string="Invoice", default="no", required=True,)
    has_purchase_subscription = fields.Selection(CATEGORY_SELECTION, string="Purchase Subscription", default="no", required=True,)

    #Line Item fields
    has_project = fields.Selection(CATEGORY_SELECTION, string="Project", default="no", required=True,)
    has_product = fields.Selection(CATEGORY_SELECTION, string="Product", default="no", required=True,)
    has_analytic = fields.Selection(CATEGORY_SELECTION, string="Analytic", default="no", required=True,)

    has_rent_vechile = fields.Selection(CATEGORY_SELECTION, string="Rent Vehicle", default="no", required=True,)
    has_travel = fields.Selection(CATEGORY_SELECTION, string="Travel", default="no", required=True,)
    has_hotel = fields.Selection(CATEGORY_SELECTION, string="Hotel", default="no", required=True,)


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

        custom_entry_type = super().create(vals)
        return custom_entry_type

    def write(self, vals):
        if 'sequence_code' in vals:
            for custom_entry_type in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if custom_entry_type.sequence_id:
                    custom_entry_type.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', custom_entry_type.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    custom_entry_type.sequence_id = sequence
        if 'company_id' in vals:
            for custom_entry_type in self:
                if custom_entry_type.sequence_id:
                    custom_entry_type.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)
    
    def create_request(self):
        self.ensure_one()
        if self.automated_sequence:
            name = self.sequence_id.next_by_id()
        else:
            name = self.name
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.custom.entry",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_name': name,
                'default_custom_entry_type_id': self.id,
                'default_user_id': self.env.user.id,
            },
        }