# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode


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
    
    task_doc_ids = fields.One2many('project.task.documents', 'task_id', string='Task Documents', copy=True, auto_join=True, )

    
class ProjectTaskDocument(models.Model):
    _name = 'project.task.documents'
    _description = 'Project Task Documents'
    
    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Name', required=True)
    task_attachment = fields.Binary(string='Attachment')
    


