# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    def action_create_serial(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.template'].browse(selected_ids)
        return {
            'name': ('Generate Serial Number'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.serial.generate',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_ids': selected_records.ids},
        }
    
    
    

