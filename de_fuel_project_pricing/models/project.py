# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'
    
    fuel_product_tmpl_id = fields.Many2one('product.template', string='Fuel Product')
        
    