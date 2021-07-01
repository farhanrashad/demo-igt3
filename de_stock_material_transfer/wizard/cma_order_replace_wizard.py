# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class StockCMAWizard(models.TransientModel):
    _name = 'stock.cma.replace.wizard'
    _description = "Replace Products Wizard"
    
    cma_order_lines = fields.One2many( 'stock.cma.replace.line.wizard', 'cma_order_id',string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Vendor', required = True)
    date_order = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now)
    
    
    @api.model
    def default_get(self,  default_fields):
        res = super(StockCMAWizard, self).default_get(default_fields)
        cma_order = self.env['stock.cma.order'].browse(self._context.get('active_ids',[]))
        condition_id = self.env['stock.cma.condition'].search([('is_default','=',True)])
        cma_order_line = []
        for line in cma_order.stock_cma_order_line:
            cma_order_line.append((0,0,{
                'product_id' : line.product_id.id,
                'replace_product_id' : line.product_id.id,
                'product_uom' : line.product_uom.id,
                'cma_order_id': line.stock_cma_order_id.id,
                'product_uom_qty' : line.product_uom_qty,
                'delivered_qty' : line.product_uom_qty,
                'stock_cma_condition_id': condition_id.id,
            }))
        res.update({'cma_order_lines':cma_order_line})
        return res
    
    def action_create_picking(self):
        self.ensure_one()
        res = self.env['stock.picking'].browse(self._context.get('id',[]))
        value = []
        return res
    
class StockCMAReplaceLine(models.TransientModel):
    _name = 'stock.cma.replace.line.wizard'
    _description = "CMA Replace line"
    
    cma_order_id = fields.Many2one('stock.cma.replace.wizard')
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    replace_product_id = fields.Many2one('product.product', string="Replacement Product", required=True)
    name = fields.Char(string="Description")
    delivered_qty = fields.Float(string='Delivered Qty', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', required=True)
    date_planned = fields.Datetime(string='Scheduled Date', default = datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('stock.cma.order.id', string='CMA Order Reference', ondelete='cascade', index=True)
    stock_cma_condition_id = fields.Many2one('stock.cma.condition', string="Condition")
	

    @api.constrains('product_uom_qty')
    def _check_quantity(self):
        if self.product_uom_qty:
            if self.product_uom_qty > self.delivered_qty:
                raise UserError(('Error!', 'The return quantity msut be less than delivered quantity '+str(self.delivered_qty)))
