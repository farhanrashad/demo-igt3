# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductSerialGenerate(models.TransientModel):
    _name = "product.serial.generate"
    _description = "Product Serial Generate"
    
    
    
    serial_count = fields.Integer(string='Number of Serial', default=1)  
    product_ids = fields.Many2many('product.template', string='Product Template')
    
    
    def action_generate_serial(self):
        for product_tmpl in self.product_ids:
            product = self.env['product.product'].search([('product_tmpl_id','=', product_tmpl.id)])
            for product_serial in range(self.serial_count):                
                serial_vals = {
                    'name': product_tmpl.categ_id.sequence_id.next_by_id(),
                    'product_id': product.id,
                    'ref': product.default_code,
                    'company_id': self.env.company.id,
                     'oem_serial_no': 1,
                }
                lot_serial = self.env['stock.production.lot'].create(serial_vals)
                
    

