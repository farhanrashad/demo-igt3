# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    next_stage_id = fields.Many2one('project.task.type', string='Next Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    prv_stage_id = fields.Many2one('project.task.type', string='Previous Stage', readonly=False, ondelete='restrict', tracking=True, index=True, copy=False)
    stage_code = fields.Char(string='Code', size=2)
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('close', 'Closed'),
    ], string='Category', default='draft')
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    next_stage_id = fields.Many2one('project.task.type', related='stage_id.next_stage_id')
    prv_stage_id = fields.Many2one('project.task.type', related='stage_id.prv_stage_id')
    stage_code = fields.Char(related='stage_id.stage_code')
    stage_category = fields.Selection(related='stage_id.stage_category')
    
    def action_submit(self):
        self.ensure_one()
        #if not self.stock_transfer_order_line:
        #    raise UserError(_("You cannot submit requisition '%s' because there is no product line.", self.name))
        self.update({
            'stage_id' : self.next_stage_id.id,
        })
        
    def action_confirm(self):
        
        self.update({
            'stage_id' : self.next_stage_id.id,
            #'date_order': fields.Datetime.now(),
        })
    def action_refuse(self):
        
        self.update({
            'stage_id' : self.prev_stage_id.id,
            #'date_order': fields.Datetime.now(),
        })

