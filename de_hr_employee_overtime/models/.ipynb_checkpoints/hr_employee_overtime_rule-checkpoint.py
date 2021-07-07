# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 

    

    
class EmployeeOvertimeRule(models.Model):
    _name = 'hr.employee.overtime.rule'
    _description = 'Employee Overtime Rule'
    _rec_name = 'overtime_type_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    

    
    overtime_type_id = fields.Many2one('hr.employee.overtime.type', string="Overtime Type", store=True)
    
    overtime_limit = fields.Float(string="Minimum hours / Shift required for Overtime Consideration", )
    tolerace_limit = fields.Float(string="Tolerance in Minutes for Overtime Hours", )
    employee_ids = fields.Many2many('hr.employee', string="Employee", store=True)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string="Date To")
    overtime_hours = fields.Float(string="Max Overtime Hours employee can avail in a Month", )
   
    
    overtime_amount = fields.Float(string="Overtime Amount As Percentage of Basic Salary", required=True)
    
    
    
    
    @api.onchange('tolerace_limit')
    def _onchange_tolerance(self):
        # avoid negative or after midnight
        self.tolerace_limit = min(self.tolerace_limit, 0.50)
        self.tolerace_limit = max(self.tolerace_limit, 0.0)
        
        
    
    @api.onchange('employee_ids')
    def onchange_employees(self):
        if self.employee_ids:
            existing_overtime_rule = self.env['hr.employee.overtime.rule'].search([('overtime_type_id','=', self.overtime_type_id.id),('type','=', self.overtime_type_id.type)])
            if existing_overtime_rule:
                for ovt in existing_overtime_rule:
                    for emp in ovt.employee_ids:
                        for employee in self.employee_ids:
                            for new_emp in employee:
                                if emp.name  == new_emp.name:
                                    raise  UserError(_(str(employee.name) + ' Already exist in ' + str(self.overtime_type_id.name) + ' Please Change Overtime Type or  Unselect this employee.'  ))

            for employee in self.employee_ids:
                employeeform = self.env['hr.employee'].search([('name','=', employee.name)])
                employeeform.update({
                    'allow_overtime' : True
                })

    
    @api.onchange('overtime_limit')
    def _onchange_hours(self):
        # avoid negative or after midnight
        self.overtime_limit = min(self.overtime_limit, 23.99)
        self.overtime_limit = max(self.overtime_limit, 0.0)

    
    
class EmployeeOvertimeRule(models.Model):
    _name = 'hr.employee.overtime.type'
    _description = 'Employee Overtime Type'

    name = fields.Char(string="Name", store=True) 
    
    type = fields.Selection([
        ('working_day', 'Working Days'),
        ('rest_day', 'Rest Days'),
        ('Gazetted', 'Gazetted Holidays'),
    ], string='Applicability',required=True )


