# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class power_prices(models.Model):
    _name = 'power.prices'
    
    power_type = fields.Many2one('product.product', 'Power Model', domain="[('sale_ok', '=', True)]", required=True)
    ip_fee_capex = fields.Float('IP Fee Power CAPEX')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')