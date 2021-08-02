# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    project_count = fields.Integer(string='Project counts', compute='_compute_project')
    task_ids = fields.One2many('project.task', 'purchase_id', string='Tasks', copy=False)
    task_count = fields.Integer(string='Task counts', compute='_compute_task_ids')

    def _get_targeted_project_ids(self):
        project_ids = []
        for project in self.order_line.project_id:
            if not project in project_ids:
                project_ids.extend(project)
        return project_ids
    
    @api.depends('project_id')
    def _compute_project(self):
        for order in self:
            order.project_count = len(order.project_id)
    
    @api.depends('task_ids')
    def _compute_task_ids(self):
        for order in self:
            order.task_count = len(order.project_id.task_ids)
            
            
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
       
        vals = {}
        vals = ({
            'name': self.name, 
            'purchase_id': self.id,
        })
        project_id = self.env['project.project'].sudo().create(vals)
        self.project_id = project_id.id
        
        templates = self.env['purchase.task.template'].search([('requisition_type_id','=',self.requisition_type_id.id)])
        #for stage in templates.stage_ids:
            #stage.update({'project_ids': [(4, project_id.id)]})
            
        stage_id = False
        projects = self._get_targeted_project_ids()
        for project in projects:
            for template in templates:
                #for stage in template.stage_ids:
                    #stage.write({'project_ids': [(4, [project.id])] })
                    #stage.project_ids = [(4, project.id)]
                    #stage.update({'project_ids': [(4, project_id.id)]})
                    
                #for stage in template.stage_ids:
                    #if not stage_id:
                        #stage_id = stage.id
                #stage_id = stages.search([('id','in',template.stage_ids)],limit=1)
                task = ({
                    'project_id': project_id.id,
                    'purchase_project_id': project.id,
                    'purchase_id': self.id,
                    'name': project.name + ' - ' + template.name,
                    'partner_id': self.partner_id.id,
                    'user_id': template.user_id.id,
                    'date_deadline': fields.Date.to_string(self.date_approve + timedelta(template.completion_days)),
                    'allow_picking': template.allow_picking,
                    'allow_invoice': template.allow_invoice,
                    'completion_days': template.completion_days,
                    'completion_percent': template.completion_percent,
                    'task_sequence': template.sequence,
                    'stage_id': stage_id,
                    'purchase_task_stage_ids': [(6, 0, template.stage_ids.ids)],
                })
                task_id = self.env['project.task'].sudo().create(task)
                task_id.update({
                    'stage_id': task_id.purchase_task_stage_ids[0].id
                })
                for tdoc in template.template_doc_ids:
                    docs = ({
                        'name': tdoc.name,
                        'task_id': task_id.id,
                    })
                    doc_id = self.env['project.task.documents'].sudo().create(docs)
        #next_stage = prv_stage = stage_id = self.env['project.task.type']        
        for stage in task_id.purchase_task_stage_ids:
            next_stage = prv_stage = stage_id = False
            stage.update({'project_ids': [(4, project_id.id)]})
            #next_stage = self.env['project.task.type'].search([('id','!=',stage.id),('project_ids','=',task_id.project_id.id)],order="sequence asc",limit=1)
            #prv_stage = self.env['project.task.type'].search([('id','!=',stage.id),('project_ids','=',task_id.project_id.id)],order="sequence desc",limit=1)
            #stage_id = self.env['project.task.type'].search([('id','!=',stage.id),('project_ids','=',task_id.project_id.id)])
            for next in task_id.purchase_task_stage_ids.filtered(lambda t: t.sequence > stage.sequence):
                next_stage = next.id
                break;
                
            for prv in task_id.purchase_task_stage_ids.filtered(lambda t: t.sequence < stage.sequence).sorted(key=lambda r: r.sequence):
                prv_stage = prv.id
                
            self.env['project.task.stage'].create({
                'task_id': task_id.id,
                'stage_id': stage.id,
                'next_stage_id': next_stage,
                'prv_stage_id': prv_stage,
            })
            
        return res

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for order in self:
            #for task in order.task_ids:
             #   task.unlink()
            order.project_id.task_ids.unlink()
            order.project_id.unlink()
        return res
    
    def _compute_proj_count(self):
        for rec in self:
            self.project_count = self.env['project.project'].search_count([('project_id', '=', self.id)])

    def action_view_project(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Project',
            'res_model': 'project.project',
            'domain': [('purchase_id', '=', self.id)],
            'context': {'create':False},
            'target': 'current',
            'view_mode': 'tree,form',
        }

    def _compute_task_count(self):
        for rec in self:
            self.task_count = self.env['project.task'].search_count([('purchase_id', '=', self.id)])

    def action_view_tasks(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Milestone',
            'res_model': 'project.task',
            'domain': [('purchase_id', '=', self.id)],
             'context': {'create':False},
            'target': 'current',
            'view_mode': 'tree,form',
        }