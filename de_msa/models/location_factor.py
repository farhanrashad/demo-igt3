# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class location_factor(models.Model):
    _name = "location.factor"
    
    state_id = fields.Many2one('res.country.state', 'Region', domain="[('country_id.name', '=', 'Myanmar')]", required=True)
    factor = fields.Float('Factor', digits=(16, 3))
    region_number = fields.Integer('Region Number')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
