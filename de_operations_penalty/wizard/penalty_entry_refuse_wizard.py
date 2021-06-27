# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class PenaltyEntryRefuse(models.TransientModel):
    _name = 'penalty.entry.refuse.wizard'
    _description = 'penalty Entry Refuse Wizard'

    penalty_entry_id = fields.Many2one('account.penalty.entry', 'penalty Entry')
    reason = fields.Text(string='Reason')
    
    
    def action_refuse(self):
        self.penalty_entry_id.update({
            'text': self.reason,
            'stage_id' : self.penalty_entry_id.stage_id.prv_stage_id.id,
        })    
    
    