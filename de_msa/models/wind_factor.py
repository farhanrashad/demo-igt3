# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class wind_factor(models.Model):
    _name = 'wind.factor'

    name = fields.Many2one('wind.factor.value', required=True)
    factor = fields.Float('Factor')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
    
    
    

    
    
class wind_factor_value(models.Model):
    _name = 'wind.factor.value'

    name = fields.Char('Name', required=True)