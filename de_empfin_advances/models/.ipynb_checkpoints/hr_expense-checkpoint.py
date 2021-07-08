# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

class HrExpenseSheetType(models.Model):
    _name = 'hr.expense.sheet.type'
    _description = 'Expense Sheet Type'
    
    name = fields.Char(string='Expense Type', required=True, translate=True)
    
class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    hr_salary_advance_id  = fields.Many2one('hr.salary.advance', string='Advances Request', domain='[("employee_id","=", employee_id), ("state","in", ("paid","close"))]')
    
    hr_expense_sheet_type_id  = fields.Many2one('hr.expense.sheet.type', string='Expense Type')
    
    total_currency_amount = fields.Float(string='Total curr.Amount', compute='_compute_curr_amount', store=True, tracking=True)
    
    @api.depends('expense_line_ids.total_amount')
    def _compute_curr_amount(self):
        for sheet in self:
            sheet.total_currency_amount = sum(sheet.expense_line_ids.mapped('total_amount'))


    
    # --------------------------------------------
    # Actions
    # --------------------------------------------

    def action_sheet_move_create(self):
        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        
        res = expense_line_ids.action_move_create()
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(lambda sheet: sheet.payment_mode == 'own_account' and sheet.expense_line_ids)
        to_post.write({'state': 'post'})
        (self - to_post).write({'state': 'done'})
        self.activity_update()
        # change status of advances
        #expense.hr_salary_advance_id.hr_expense_sheet_id = self.id
        for expense in expense_line_ids:
            #expense.hr_salary_advance_id.state = 'close'
            expense.advance_line_id.state = 'close'
            #expense.hr_salary_advance_id.hr_expense_id = expense.id
            #expense.hr_salary_advance_id.hr_expense_id = expense.id
        return res
    
class HrExpenseType(models.Model):
    _name = 'hr.expense.type'
    _description = 'Expense Type'
    
    name = fields.Char(string='Expense Category', required=True, translate=True)

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    #hr_salary_advance_id  = fields.Many2one('hr.salary.advance', string='Advances Request', domain='[("employee_id","=", employee_id), ("state","in", ("paid","close"))]')

    hr_salary_advance_id  = fields.Many2one('hr.salary.advance', string='Advances Request', )
    advance_line_id  = fields.Many2one('hr.salary.advance.line', string='Advances Line', domain='[("advance_id","=", hr_salary_advance_id)]')
    hr_expense_sheet_type_id  = fields.Many2one('hr.expense.sheet.type', related='sheet_id.hr_expense_sheet_type_id')
    expense_type_id = fields.Many2one('hr.expense.type', string='Expense Category', copy=False)

    
    #@api.depends('product_id', 'company_id')
    def _compute_from_product_id_company_id(self):
        for expense in self.filtered('product_id'):
            expense = expense.with_company(expense.company_id)
            expense.name = expense.name or expense.product_id.display_name
            if not expense.attachment_number or (expense.attachment_number and not expense.unit_amount):
                expense.unit_amount = expense.unit_amount
            expense.product_uom_id = expense.product_id.uom_id
            expense.tax_ids = expense.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == expense.company_id)  # taxes only from the same company
            account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                expense.account_id = account
    
    
    
    @api.onchange('hr_salary_advance_id')
    def onchange_advaces(self):
        if self.hr_salary_advance_id:
            self.update({
                'name': self.hr_salary_advance_id.name, 
                #'product_id': self.hr_salary_advance_id.product_id.id,
                'unit_amount': self.hr_salary_advance_id.amount_total,
                'currency_id': self.hr_salary_advance_id.currency_id,
                'quantity': 1,
                'payment_mode': 'own_account',
            })

