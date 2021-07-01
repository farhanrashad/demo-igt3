# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = 'project.project'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project Task with Purchase Order'
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False), ('is_closed', '=', False)])

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order', readonly=True)
    purchase_project_id = fields.Many2one('project.project', string='Site')
    
    purchase_task_stage_ids = fields.Many2many('project.task.type', string='Stages', readonly=True)
    
    allow_picking = fields.Boolean(string='Allow on Picking', help='User will provide the milestone on picking with purchase order reference')
    allow_invoice = fields.Boolean(string='Allow on invoice', help='User will provide the milestone on invoice with purchase order reference')


