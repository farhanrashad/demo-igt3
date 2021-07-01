# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
   
    def get_shipment_count(self):
        count = self.env['stock.picking'].search_count([('move_id', '=', self.id)])
        self.shipment_count = count
        
    shipment_count = fields.Integer(string='Invocie Count', compute='get_shipment_count')
    
    
    
    
    def action_view_shipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Invocies',
            'domain': [('move_id','=', self.id)],
            'target': 'current',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
        }

    
    
 

    
    
    
    
    
