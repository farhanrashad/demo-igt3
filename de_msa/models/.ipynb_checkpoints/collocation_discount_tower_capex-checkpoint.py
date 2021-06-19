# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class collocation_discount_tower_capex(models.Model):
    _name = "collocation.discount.tower.capex"
    
    year = fields.Integer('Year', required=True)
    factor_for_1 = fields.Float('Factor for 1 Tenant')
    factor_for_2 = fields.Float('Factor for 2 Tenants')
    factor_for_3 = fields.Float('Factor for 3 Tenants')
    factor_for_4 = fields.Float('Factor for 4 Tenants')
    factor_for_5 = fields.Float('Factor for 5 Tenants')
    factor_for_6 = fields.Float('Factor for 6 Tenants')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
