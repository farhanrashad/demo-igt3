# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class msa_penalty(models.Model):
    _name = "msa.penalty"
    
    
    name = fields.Char('Name', required=True)
    penalties = fields.Float('Penalties (%)')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')