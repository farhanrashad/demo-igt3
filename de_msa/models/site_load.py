# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class site_load(models.Model):
    _name = 'site.load'

    power_type = fields.Many2one('product.product', 'Power Model', domain="[('sale_ok', '=', True),('is_product_category_power', '=', True)]", required=True)
    msa_id = fields.Many2one('master.service.agreement', 'MSA')
    access_low = fields.Float('Access Low')
    access_high = fields.Float('Access High')
    dwdm = fields.Float('DWDM')
    standard_hub = fields.Float('Standard Hub')
