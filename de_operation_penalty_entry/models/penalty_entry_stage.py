# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class AccountPenaltyEntryStage(models.Model):
    _name = 'account.penalty.entry.stage'
    _description = 'Penalty Entry Stage'
    _order = 'sequence, id'

    def _get_default_penalty_entry_type_ids(self):
        default_penalty_entry_type_id = self.env.context.get('default_penalty_entry_type_id')
        return [default_penalty_entry_type_id] if default_penalty_entry_type_id else None
    
    name = fields.Char(string='Stage Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the stage without removing it.")

    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this stage. It will appear "
                             "as a tooltip over the stage's name.", translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    penalty_entry_type_ids = fields.Many2many('account.penalty.entry.type', 'penalty_entry_type_stage_rel', 'penalty_entry_stage_id', 'penalty_entry_type_id', string='Entry Types',
        default=_get_default_penalty_entry_type_ids)
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('confirm', 'Confirmed'),
        ('closed', 'Closed'),
    ], string='Category', default='draft')
    
    next_stage_id = fields.Many2one('account.penalty.entry.stage', string='Next Stage', copy=False)
    prv_stage_id = fields.Many2one('account.penalty.entry.stage', string='Previous Stage', copy=False)

