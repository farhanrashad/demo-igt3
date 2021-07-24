# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class CustomEntryRefuse(models.TransientModel):
    _name = 'entry.correction.reason'
    _description = 'Entry Correction Reason'

    custom_entry_id = fields.Many2one('account.custom.entry', 'Custom Entry')
    reason = fields.Text(string='Correction Reason', required=True)
    
    
    def action_correction(self):
        self.custom_entry_id.update({
            'correction_reason': self.reason,
            'is_custom_entry_import': True,
        })    
    
    