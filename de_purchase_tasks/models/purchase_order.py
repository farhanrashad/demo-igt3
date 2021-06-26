from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Project')
    task_ids = fields.Many2many('project.task', string='Project Task')
    project_count = fields.Integer('Project Count', compute='_compute_proj_count')
    task_count = fields.Integer('Task Count', compute='_compute_task_count')

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        vals = {
            'name': self.name,
            'purchase_order_id': self.id,
        }
        project_id = self.env['project.project'].create(vals)
        self.project_id = project_id.id
        # raise UserError(res)
        return res

    def _compute_proj_count(self):
        for rec in self:
            self.project_count = self.env['project.project'].search_count([('purchase_order_id', '=', self.id)])

    def get_Project(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Project',
            'res_model': 'project.project',
            'domain': [('purchase_order_id', '=', self.id)],
            'target': 'current',
            'view_mode': 'tree,form',
        }

    def _compute_task_count(self):
        for rec in self:
            self.task_count = self.env['project.task'].search_count([('purchase_order_id', '=', self.id)])

    def get_Task(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Task',
            'res_model': 'project.task',
            'domain': [('purchase_order_id', '=', self.id)],
            'target': 'current',
            'view_mode': 'tree,form',
        }