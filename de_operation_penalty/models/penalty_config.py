# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
#from datetime import date
from datetime import datetime, timedelta


#Penlaty Configiguration
class PenaltyConfig(models.Model):
    _name = 'op.penalty.config'
    _description = 'Operations Penalty Config'
    
    name = fields.Char(string='Name', compute='_compute_name', translate=True)
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the stage without removing it.")

    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this penalty.", translate=True)
    
    partner_id = fields.Many2one('res.partner',  String="Supplier")
    effective_date = fields.Date(string='Effective From')
    
    penalty_config_line = fields.One2many('op.penalty.config.line', 'penalty_config_id', string='Penalty Config Line', copy=True, auto_join=True)
    
    @api.depends('partner_id','effective_date')
    def _compute_name(self):
        for record in self:
            record.name = record.partner_id.name
    
class PenaltyConfigLine(models.Model):
    _name = 'op.penalty.config.line'
    _description = 'Penalty Configuration SLA Line'
    
    penalty_config_id = fields.Many2one('op.penalty.config', string='Penalty Config', required=True, ondelete='cascade', index=True, copy=False)
    service_class = fields.Selection([
        ('a', 'Critical Site'), 
        ('b', 'Class B'), 
        ('c', 'Class C')], default='a', string='Classification')
    service_level = fields.Selection([
        ('critical', 'Critical'), 
        ('major', 'Major'), 
        ('minor', 'Minor'), 
        ('normal', 'Normal')], default='normal', string='Service Level')
    uptime_from = fields.Float(string='Uptime From', default=0.0)
    uptime_to = fields.Float(string='Uptime To', default=0.0)
    penalty_deduction_per = fields.Float(string='Penalty %age', default=0.0)
    penalty_deduction_factor = fields.Float(string='Factor', default=0.0)


