# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class capex_escalation(models.Model):
    _name = "capex.escalation"
  
    year = fields.Char('Year', required=True, size=4)
    cpi = fields.Float('CPI')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
