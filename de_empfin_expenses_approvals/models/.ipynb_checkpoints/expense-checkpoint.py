# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class HRExpenseType(models.Model):
    _inherit = 'hr.expense.type'
    
    group_id = fields.Many2one('res.groups', string='Security Group')
    
class HRExpense(models.Model):
    _inherit = 'hr.expense'

class HRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Line Manager Approval'),
        ('approval1', 'Expense Category Approval'),
        ('approval2', 'Finanace Approval'),
        ('approve', 'Waiting Account Entries'),
        ('post', 'Waiting Payment'),
        ('done', 'Paid'),
        ('cancel', 'Refused')
    ], string='Status', index=True, readonly=True, tracking=True, copy=False, default='draft', required=True, help='Expense Report State')
    
    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id    
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        sheet_to_approve = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if sheet_to_approve:
            notification['params'].update({
                'title': _('The expense reports were successfully approved by manager.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            sheet_to_approve.write({'state': 'approval1', 'user_id': responsible_id})
        self.activity_update()
        return notification
    
    def approve_cateegory_expense_sheets(self):
        responsible_id = self.user_id.id or self.env.user.id
        for expense in self.expense_line_ids:
            group_id = expense.expense_type_id.group_id
            if group_id:
                if (group_id & self.env.user.groups_id):
                    expense.write({'state': 'approved', })
                    
        expenses = self.mapped('expense_line_ids').filtered(
                lambda expense: expense.state in ('draft','reported')
            )
        if not expenses:
            self.write({'state': 'approval2', 'user_id': responsible_id})
            
                #if not (group_id & self.env.user.groups_id):
                    #raise UserError(_("You are not authorize to approve expense category '%s'.", order.custom_entry_type_id.name))