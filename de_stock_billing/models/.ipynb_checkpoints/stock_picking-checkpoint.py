# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    invoice_control = fields.Selection([('invoiced', 'Invoiced'),
                                           ('2binvoice', 'To Be Invoiced'),
                                            ('none', 'Not Applicable'),
                                           ], string="Invoice Control", default='2binvoice')
    
    move_id = fields.Many2one('account.move', string='Invoice')
    
    def get_invocie_count(self):
        count = self.env['account.move'].search_count([('invoice_origin', '=', self.name)])
        self.invocie_count = count
        
    invocie_count = fields.Integer(string='Invocie Count', compute='get_invocie_count')
    
    
    
    
    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Invocies',
            'domain': [('invoice_origin','=', self.name)],
            'target': 'current',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
        }

    
    
    def action_create_invoice(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['stock.picking'].browse(selected_ids)
        return {
            'name': ('Create Draft Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.invoice.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_picking_ids': selected_records.ids},
        }
    


    
    
    
    

    
    
    
    
    
