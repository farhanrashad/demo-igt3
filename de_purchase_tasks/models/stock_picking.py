# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    task_id = fields.Many2one('project.task', string='Milestone', domain="[('purchase_id', '=', purchase_id),('allow_picking', '=', allow_picking),('stage_id.is_closed','=',True)]", copy=False)
    allow_picking = fields.Boolean(string='Allow on Picking', compute="_compute_allow_picking")
    
    @api.depends('purchase_id')
    def _compute_allow_picking(self):
        ap = False
        for task in self.purchase_id.task_ids:
            if task.allow_picking:
                ap = task.allow_picking
        self.allow_picking = ap
        
    @api.onchange('task_id')
    def _onchange_task_id(self):
        for picking in self:
            if picking.task_id.completion_percent > 0:
                for line in picking.move_ids_without_package:
                    line.quantity_done = (picking.task_id.completion_percent / 100) * line.purchase_line_id.product_qty