# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class tower_without_power(models.Model):
    _name = 'tower.without.power'
    
    tower_type = fields.Many2one('product.product', 'Tower Type', domain="[('sale_ok', '=', True)]", required=True)
    ip_fee_capex = fields.Float('IP Fee For CAPEX')
    ip_fee_opex = fields.Float('IP Fee For OPEX')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
    