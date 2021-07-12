# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta

import json
from lxml import etree

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'),('12', 'Dec')]

class CustomEntry(models.Model):
    _inherit = 'account.custom.entry'
    
    #Line Item fields
    has_hse_fields = fields.Selection(related="custom_entry_type_id.has_hse_fields")
    has_pm_fields = fields.Selection(related="custom_entry_type_id.has_pm_fields")
    has_sla_fields = fields.Selection(related="custom_entry_type_id.has_sla_fields")
    has_spmrf_fields = fields.Selection(related="custom_entry_type_id.has_spmrf_fields")
    
class CustomEntryLine(models.Model):
    _inherit = 'account.custom.entry.line'
    
    #sla
    service_class = fields.Selection([
        ('a', 'Critical Site'), 
        ('b', 'Class B'), 
        ('c', 'Class C')], default='a', string='Classification')
    service_level = fields.Selection([
        ('critical', 'Critical'), 
        ('major', 'Major'), 
        ('minor', 'Minor'), 
        ('normal', 'Normal')], default='normal', string='Service Level')
    uptime = fields.Float(string='Uptime', default=0.0)
    #occurence
    #sow
    penalty_sow_type_id = fields.Many2one('op.penalty.config.sow.type', string='SOW Type')
    penalty_sow_id = fields.Many2one('op.penalty.config.sow', string='SOW')
    frequency = fields.Char(related='penalty_sow_id.frequency')
    sow_deduct_type = fields.Selection([
        ('a', 'A'), 
        ('b', 'B'), 
        ], default='a', string='Deduction Type')
    