from odoo import models, fields, api, _
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 
from datetime import datetime


class HrPayslipsInherit(models.Model):
    _inherit = 'hr.payslip'
    
    
    def action_payslip_done(self):
        
        res = super(HrPayslipsInherit, self).action_payslip_done()
        overtime_amount = self.env['hr.employee.overtime'].search([('name','=', self.employee_id.id),('check_in','>=', self.date_from),('check_out','<=', self.date_to),('state','=','approved')])
        for overtime_line in overtime_amount:
            overtime_line.update({
               'state': 'paid',
                  }) 
        return res
    
    def compute_sheet(self):
#         for other_input in self.input_line_ids:
#             other_input.unlink()
        other_inputs = self.env['hr.payslip.input.type'].search([('code','=', 'AOVT')])
        overtime_amount = self.env['hr.employee.overtime'].search([('name','=', self.employee_id.id),('check_in','>=', self.date_from),('check_out','<=', self.date_to),('state','=','approved')])
        overtime_rule = self.env['hr.employee.overtime.rule'].search([('employee_ids','=', self.employee_id.id),('date_from','>=', self.date_from),('date_to','<=', self.date_to)])

        data = []
        amount = 0
        for input in other_inputs:
            if overtime_amount:
                for overtime in overtime_amount:
                    for rule in overtime_rule:
                        if rule.overtime_type == 'fixed':
                            amount = amount + (rule.overtime_amount * overtime.overtime_hours)
                        elif rule.overtime_type == 'percent':
                            amount = amount + (rule.overtime_amount * overtime.overtime_hours)
                data.append((0,0,{
                                'payslip_id': self.id,
                                'sequence': 1,
                                'code': input.code,
                                'contract_id': self.contract_id.id,
                                'input_type_id': input.id,
                                'amount': amount,
                                }))
        self.input_line_ids = data
        res = super(HrPayslipsInherit, self).compute_sheet()
        
        return res
    
    

    
    

            
            