# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    stock_transfer_order_id = fields.Many2one('stock.transfer.order', string='Transfer Order', copy=False)
    
    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                    'stock_transfer_order_id': picking.stock_transfer_order_id.id
                })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                moves_to_backorder.write({
                    'picking_id': backorder_picking.id,
                    'stock_transfer_order_line_id': moves_to_backorder.stock_transfer_order_line_id.id,
                })
                moves_to_backorder.mapped('package_level_id').write({
                    'picking_id':backorder_picking.id,
                })
                moves_to_backorder.mapped('move_line_ids').write({
                    'picking_id': backorder_picking.id,
                })
                backorders |= backorder_picking
        return backorders
    
    
class StockMove(models.Model):
    _inherit = 'stock.move'
   
    def _get_default_condition(self):
        condition_id = self.env['stock.transfer.material.condition'].search([('is_default','=',True)], limit=1)
        return condition_id
    
    stock_transfer_order_line_id = fields.Many2one('stock.transfer.order.line')
    stock_transfer_return_line_id = fields.Many2one('stock.transfer.return.line')
    stock_material_condition_id = fields.Many2one('stock.transfer.material.condition', string="Condition", default=_get_default_condition)
    
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    stock_transfer_order_id = fields.Many2one('stock.transfer.order', compute='_compute_transfer_order')
    
    @api.depends('picking_id')
    def _compute_transfer_order(self):
        for line in self:
            if line.picking_id.stock_transfer_order_id:
                line.stock_transfer_order_id = line.picking_id.stock_transfer_order_id.id
            else:
                line.stock_transfer_order_id = False
            
    #@api.onchange('product_id')
    #def _onchange_product_id(self):
        #for line in self:
            #if line.picking_id.stock_transfer_order_id:
                #line.location_dest_id = line.move_id.stock_transfer_order_line_id.location_dest_id.id
                
    #@api.model_create_multi
    #def create(self, vals_list):
        #for vals in vals_list:
            #if vals.get('move_id'):
                #vals['company_id'] = self.env['stock.move'].browse(vals['move_id']).company_id.id
            #elif vals.get('picking_id'):
                #vals['company_id'] = self.env['stock.picking'].browse(vals['picking_id']).company_id.id
            #vals['location_dest_id'] = self.env['stock.move'].browse(vals['move_id']).stock_transfer_order_line_id.location_dest_id.id

        #mls = super().create(vals_list)
