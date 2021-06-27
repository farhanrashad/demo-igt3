from odoo import fields, models, _, api
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project Task with Purchase Order'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase ID', related='project_id.purchase_order_id')
    po_count = fields.Integer('PO Count', compute='_compute_po_count')
    generate_boolean = fields.Boolean(compute='_compute_boolean', default=False)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.name == 'Confirm':
            if not self.partner_id:
                raise UserError("Please Select A Vendor!!!!!")
            vals = {
                'origin': self.name,
                'partner_id': self.partner_id.id,
                'partner_ref': None,
                'order_line': False,
                # 'date_order':self.date_deadline,
                'state': 'draft',}
            move = self.env['purchase.order'].create(vals)
            self.purchase_order_id = move.id
            vals={
                'name':move.name,
                'purchase_order_id':move.id,
            }
            project_id = self.env['project.project'].create(vals)

    def _compute_po_count(self):
        for rec in self:
            self.po_count = self.env['purchase.order'].search_count([('origin', '=', rec.name)])

    def _compute_boolean(self):
        for rec in self:
            if rec.po_count > 0:
                self.generate_boolean = True
            else:
                self.generate_boolean = False

    def get_PurchaseOrder(self):
        """
        To get Count against Project Task for Different PO
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'domain': [('origin', '=', self.name)],
            'target': 'current',
            'view_mode': 'tree,form',
        }
