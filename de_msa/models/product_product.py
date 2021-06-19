# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta



class ProductProductInh(models.Model):
    _inherit = 'product.product'
    
    is_product_category_power = fields.Boolean('Is Category Power?')
    is_product_category_tower = fields.Boolean('Is Category Tower?')
