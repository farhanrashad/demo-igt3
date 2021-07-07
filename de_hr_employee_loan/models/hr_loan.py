# -*- coding: utf-8 -*-

import math
from odoo import models, fields, api,_
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError



class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department")
    installment = fields.Integer(string="No. of Installment")
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today())
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    emp_account_id = fields.Many2one('account.account', string="Loan Account")
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
    loan_amount = fields.Float(string="Loan Amount", required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount')
    service_time = fields.Integer(string='Service Time', defualt=0)
#     crnt_date = fields.Date(string="Current Date", default=fields.Date.today())
    
    loan_type = fields.Selection([
        ('special_loan', 'Special Loan'),
        ('loan_beyond_policy', 'Loan Beyond Policy'),
        ('loan_against_pfund', 'Loan Against P.Fund'),

    ], string="Loan Type", default='special_loan')
   
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    

    @api.onchange('employee_id')
    def _compute_service_time(self):
        if self.loan_type != 'loan_beyond_policy':
            total_days = 0
            employee_record = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            for employee in employee_record:
                if not employee.date:
                    raise UserError(('Date of Joining is Missing'))
                delta = self.payment_date - employee.date
                total_days = delta.days
            self.service_time = total_days

            for emp in employee_record:
                if emp.grade_type.name != 'Management':
                    raise UserError(('You are not Eligible, Only Management Staff Avail This Facility'))

                if emp.emp_type != 'permanent' and emp.emp_type != 'contractor':
                    raise UserError(('You are not Eligible, Only Permanent & Contractual Staff Avail This Facility'))
                    
                    
    @api.constrains('date')
    def check_current_date(self):
        total_days = 0
        crnt_date = date.today()
        loan = self.search([('employee_id', '=', self.employee_id.id),('state', 'in', ['draft','waiting_approval_1','approve'])],order="date desc",limit=1)
        if loan:
            for emp in loan:
                delta = emp.date - crnt_date
                total_days = delta.days
                if total_days < 1095:
                    raise UserError(('You Can Avail This Facility Once In A Three Years'))
                    
#     attendance_test.search([('employee_id','=',employee.id),('timestamp','>=',date_start),('timestamp','<=',date_end),('is_attedance_created','=',False)], order="timestamp desc",limit=1)
        

    @api.constrains('service_time')
    def _check_time(self):
        if self.loan_type != 'loan_beyond_policy':
            if self.service_time < 730:
                raise UserError(('You Cannot Avail This Facility, Your Service Period is Less Than Two Years'))
            
    @api.onchange('installment')
    def check_installment(self):
        if self.installment > 12:
            raise UserError(('You Can Make a Maximum of 12 Installments Per Loan'))

    
    @api.onchange('loan_amount')
    def check_loan_amount(self):
        if self.loan_type != 'loan_beyond_policy':
            employee_record = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            contract_record = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
            if contract_record:
                for employee in contract_record:
                    wage = employee.wage
                    contract_wage = employee.wage/2
                    permanent_wage = employee.wage*2
                for emp in employee_record:                
                    if emp.emp_type == 'contractor':
                        if self.loan_amount > contract_wage:  
                            raise UserError(('Contractual Employee Can Avail 50% of His Salary'))
                    if emp.emp_type == 'permanent':
                        if self.loan_amount > permanent_wage:
                            raise UserError(('Permanent Employee Can Avail UpTo Double of His Salary'))
                
        

    @api.model
    def create(self, values):
            
        loan_count = self.env['hr.loan'].search_count([('employee_id', '=', values['employee_id']), ('state', '=', 'approve'),
                                                       ('balance_amount', '!=', 0)])
#         if loan_count:
#             raise UserError(('The employee has already a pending installment'))
#         else:
        values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        res = super(HrLoan, self).create(values)
        return res

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        self.write({'state': 'approve'})
        
    def unlink(self):
        for leave in self:
            if leave.state in ('waiting_approval_1','waiting_approval_2','approve','refuse','cancel'):
                raise UserError(_('You cannot delete a request which is not  at Draft State'))
    
            return super(HrLoan, self).unlink()
    
    # compute lines

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for other_input in self.loan_lines:
            other_input.unlink()    
            
        for loan in self:
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = float(loan.loan_amount) / float(loan.installment)
            for i in range(0,self.installment):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
    


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    opening_bal = fields.Float("Opening Balance")
    closing_bal = fields.Float("Closing Balance")
    
    

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
