# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class AdvanceAgainstExpenses(models.Model):
    _inherit = 'advance.against.expense'
    _description = 'Advance Against Expenses Inh'
    
    
    category_id = fields.Many2one('approval.category', related='employee_id.adv_exp_id')
    approval_request_id = fields.Many2one('approval.request', string="Approval")
    
            
    def action_reject(self):
        for line in self:
            line.update({
                'state': 'reject'
            })
            adv_exp_approval = self.env['approval.request'].search([('exp_adv_id','=', line.id)], limit=1)
            adv_exp_approval.action_cancel()
            
            
    @api.model
    def create(self, vals):
        sheet = super(AdvanceAgainstExpenses, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)).create(vals)
        if sheet.category_id:
            sheet.action_create_approval_request_adv_exp()
        return sheet
    
    
    def action_create_approval_request_adv_exp(self):
        approver_ids  = []
        request_list = []

        for line in self:
            if line.category_id:
                request_list.append({
                        'name': line.employee_id.name + ' Has Advance Against Expense Request ref '+str(line.name)+' sum of amount '+str(line.amount),
                        'request_owner_id': line.employee_id.user_id.id,
                        'category_id': line.category_id.id,
                        'exp_adv_id': line.id,
                        'reason': line.employee_id.name + ' Has Advance Against Expense Request ref '+str(line.name)+' sum of amount '+str(line.amount),
                        'request_status': 'new',
                })
                approval_request_id = self.env['approval.request'].create(request_list)
                approval_request_id._onchange_category_id()
                approval_request_id.action_confirm()
                line.approval_request_id = approval_request_id.id
                