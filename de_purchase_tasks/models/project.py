# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    allow_milestone = fields.Boolean(string='Allow for Milestone', default=False)
    submission_type = fields.Selection(
        [('0', 'Normal'), ('1', 'Document Submission'), ('2', 'Invoice Submission')], string='Partner Submission', default='0')

class Project(models.Model):
    _inherit = 'project.project'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
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
    completion_days = fields.Integer(string='Completion Days', readonly=True)
    completion_percent = fields.Float(string='Completion Percentage', readonly=True)
    delivery_assigned = fields.Boolean(string='Delivery Assigned', readonly=True)
    task_sequence = fields.Integer(string='Task Sequence', readonly=True)
    date_estimated = fields.Datetime(string='Estimated Completion Date', compute="_compute_date_completion")
    days_to_close = fields.Integer(string='Delay', compute="_compute_days_to_close")
    picking_id = fields.Many2one('stock.picking', string='Picking', compute="_compute_picking")
    
    date_doc_submission = fields.Date(string='Docs Submit On', compute="_compute_all_submission_date", store=True)
    date_inv_submission = fields.Date(string='Invoice Submit On', compute="_compute_all_submission_date", store=True)
    
    task_doc_ids = fields.One2many('project.task.documents', 'task_id', string='Task Documents', copy=True, auto_join=True, )

    def _compute_date_completion(self):
        dt = False
        for task in self:
            if task.purchase_id:
                dt = fields.Date.to_string(task.purchase_id.date_approve + timedelta(task.completion_days))
            task.date_estimated = dt
    
    def _compute_picking(self):
        picking = self.env['stock.picking']
        for task in self:
            picking = self.env['stock.picking'].search([('task_id','=',task.id)],limit=1)
            task.picking_id = picking.id
            
    def _compute_days_to_close(self):
        days = 0
        for task in self:
            days = 0
            if not task.stage_id.is_closed:
                if task.purchase_id.date_approve:
                    days = (fields.Datetime.now() - task.purchase_id.date_approve).days
            task.days_to_close = days
    
    @api.depends('stage_id')
    def _compute_all_submission_date(self):
        dt1 = dt2 = False
        for task in self:
            if task.stage_id.submission_type == '1':
                dt1 = task.date_last_stage_update
            elif task.stage_id.submission_type == '2':
                dt2 = task.date_last_stage_update
            
            if not dt1:
                dt1 = task.date_doc_submission
            if not dt2:
                dt2 = task.date_inv_submission
            
        task.date_doc_submission = dt1
        task.date_inv_submission = dt2
                
        
class ProjectTaskDocument(models.Model):
    _name = 'project.task.documents'
    _description = 'Project Task Documents'
    
    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Name', required=True)
    task_attachment = fields.Binary(string='Attachment')
    


