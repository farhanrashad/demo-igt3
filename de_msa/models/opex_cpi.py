# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class opex_cpi(models.Model):
     
    _name = "opex.cpi"
    
    year = fields.Char('Year', required=True, size=4)
    cpi = fields.Float('CPI')
    msa_id =fields.Many2one('master.service.agreement', 'Master Service Agreement')
    cpio = fields.Float('Ooredoo CPI rate')