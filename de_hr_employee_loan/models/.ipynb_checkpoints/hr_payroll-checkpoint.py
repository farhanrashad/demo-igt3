# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_total_paid(self):
        """This compute the total paid amount of Loan.
            """
        total = 0.0
        for line in self.loan_ids:
            if line.paid:
                total += line.amount
        self.total_paid = total

    loan_ids = fields.One2many('hr.loan.line', 'payslip_id', string="Loans")
    total_paid = fields.Float(string="Total Loan Amount", compute='compute_total_paid')


    def get_loan(self):
        """This gives the installment lines of an employee where the state is not in paid.
            """
        loan_list = []
        loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', self.employee_id.id), ('paid', '=', False)])
        for loan in loan_ids:
            if loan.loan_id.state == 'approve':
                loan_date = str(loan.date).split('-')
                today = str(date.today()).split('-')
                loan_year_month = loan_date[0]+'-'+loan_date[1]
                today_year_month = today[0]+'-'+today[1]
#                 if(today_year_month == loan_year_month):
#                     loan.update({'paid':True})
                loan_list.append(loan.id)
        self.loan_ids = loan_list
        return loan_list

    def action_payslip_done(self):
        
        loan_list = []
        loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', self.employee_id.id), ('paid', '=', False)])
        for loan in loan_ids:
            if loan.loan_id.state == 'approve':
                loan_date = str(loan.date).split('-')
                today = str(self.date_from).split('-')
                loan_year_month = loan_date[0]+'-'+loan_date[1]
                today_year_month = today[0]+'-'+today[1]
                if(today_year_month == loan_year_month):
                    loan.update({'paid':True,'opening_bal':loan.loan_id.balance_amount,'closing_bal':loan.loan_id.balance_amount-loan.amount})
        
        for line in self.loan_ids:
            if line.paid:
                loan_list.append(line.id)
            else:
                line.payslip_id = False
        self.loan_ids = loan_list
        return super(HrPayslip, self).action_payslip_done()





    def compute_sheet(self):
        amount = 0 
        loan_exists = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id),
                                                        ('state', '=', 'approve')])
        
        if loan_exists:
            for loan in loan_exists.loan_lines:
                current_date = datetime.strptime(str(self.date_from), '%Y-%m-%d').date().month
                loan_date = loan.date
                existing_date = datetime.strptime(str(loan_date), '%Y-%m-%d').date().month
                if current_date == existing_date:
                    amount = loan.amount
            
                    input_exists = self.env['hr.payslip.input'].search([('payslip_id', '=', self.id), ('code', '=', 'LO')])
                                
                    if not input_exists:
                        input_type_exists = self.env['hr.payslip.input.type'].search([('code', '=', 'LO')])
            
                        input_exists.create({
                            'input_type_id': input_type_exists.id,
                            'code': 'LO',
                            'amount': amount,
                            'contract_id': self.contract_id.id,
                            'payslip_id': self.id,
                        })
                    else:
                        input_exists.write({
                            'amount': amount,
                        })
        rec = super(HrPayslip, self).compute_sheet()
        return rec
            