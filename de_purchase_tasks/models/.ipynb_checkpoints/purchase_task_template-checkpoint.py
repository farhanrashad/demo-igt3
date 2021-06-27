# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseTaskTemplate(models.Model):
    _name = 'purchase.task.template'
    _description = 'Purchase Task Template'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(default=1)
    requisition_type_id = fields.Many2one('purchase.requisition.type', string="Requisition Type", required=True, )
    completion_days = fields.Integer(string='Completion Days')
    stage_ids = fields.Many2many('project.task.type', string='Stages')
    allow_picking = fields.Boolean(string='Allow on Picking', help='User will provide the milestone on picking with purchase order reference')
    allow_invoice = fields.Boolean(string='Allow on invoice', help='User will provide the milestone on invoice with purchase order reference')

    user_id = fields.Many2one('res.users', string='Responsible', index=True, default=lambda self: self.env.user, check_company=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    template_doc_ids = fields.One2many('purchase.task.template.docs', 'purchase_task_template_id', string='Docs', copy=True)

    
class PurchaseTaskTemplateDocs(models.Model):
    _name = 'purchase.task.template.docs'
    _description = 'Purchase Task Template docs'
    
    name = fields.Char("Name", required=True)
    purchase_task_template_id = fields.Many2one('purchase.task.template', string='Template', index=True, required=True, ondelete='cascade')
