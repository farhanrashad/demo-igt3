# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo import exceptions 
from odoo.exceptions import UserError, ValidationError 




class HrEmployee(models.Model):
    _inherit = 'hr.department'
    
    allow_overtime = fields.Boolean(string="Allow Overtime")

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    @api.model
    def cron_create_overtime(self):
        if self.employee_id.allow_overtime == True:
            vals = {
                'name': self.employee_id.id,
                'date':  self.check_in,
                'check_in': self.check_in,
                'check_out': self.check_in,
                'total_hours': self.worked_hours,
                'overtime_hours': self.worked_hours - self.employee_id.resource_calendar_id.hours_per_day,
                }
            overtime_lines = env['hr.employee.overtime'].create(vals) 
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
     
    allow_overtime = fields.Boolean(string='OT Allowed', )
    
    
class EmployeeOvertime(models.Model):
    _name = 'hr.employee.overtime'
    _description = 'Employee Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'employee_id'
    
    def unlink(self):
        for leave in self:
            if leave.state in ('to_approve','approved','paid'):
                raise UserError(_('You cannot delete an order form  which is not draft or close. '))
     
            return super(EmployeeOvertime, self).unlink()
        
    def action_approve(self):
        overtime_rule = self.env['hr.employee.overtime.rule'].search([('employee_ids','=', self.name.id)])
        for rule in overtime_rule:
            if rule.overtime_hours < self.overtime_hours:
                raise UserError(_('Overtime exceeded for the internal.'))
            else:                
                self.write ({
                        'state': 'approved'
                    })
        
    def action_confirm(self):
        self.write ({
                'state': 'to_approve'
            })    
        
    def action_refuse(self):
        self.write ({
                'state': 'refused'
            })
        
    def action_draft(self):
        self.write ({
                'state': 'draft'
            })    
    
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True)
    date = fields.Date(string='Date', required=True)
    month = fields.Integer(string="Month No.")
    check_in = fields.Datetime(string="Check In", readonly=True)
    check_out = fields.Datetime(string="Check Out", readonly=True)
    total_hours = fields.Float(string="Total Hours", readonly=True)
    overtime_type = fields.Char(string="Overtime Type")
    overtime_hours = fields.Float(string="Overtime Hours", readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('to_approve', 'To Approve'),
        ('refused', 'Refused'),
        ('approved', 'Approved'),        
        ('paid', 'Paid'),
        ('close', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    

    
