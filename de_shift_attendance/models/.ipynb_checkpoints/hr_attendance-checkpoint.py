# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
   
    def _default_employee(self):
        return self.env.user.employee_id
    

    date = fields.Date(string="Date", default=fields.date.today())
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    shift_type_id = fields.Many2one('hr.shift', string="Shift Type")
    shift_time_in = fields.Float(string="Shift Time In", )
    shift_time_out = fields.Float(string="Shift Time Out")
    overtime_hours = fields.Float(string='Overtime Hours', compute='_compute_overtime_hours', store=True, readonly=True)
    entry_type = fields.Char(string="Entry Type")
    is_overtime = fields.Boolean(string="Is Overtime")
    
    
    
    def  action_employee_overtime(self):
        HrShiftAttendance = self.env['hr.attendance'].search([('is_overtime','=', False)])
        for line in HrShiftAttendance:
            employee_id = line.employee_id.id
            overtime_hours = line.overtime_hours
            date = line.date 
            check_in = line.check_in 
            month = line.check_in.month 
            check_out = line.check_out 
            work_hours = line.worked_hours 
            overtime_hours = line.overtime_hours 
            overtime_rule = self.env['hr.employee.overtime.rule'].search([])
            for rule in overtime_rule:
                max_overtime_allow = rule.overtime_hours
                ovt_type = rule.overtime_type_id.name
                tolerance_time = rule.tolerace_limit
                overtime_limit = rule.overtime_limit 
                max_overtime = overtime_limit - tolerance_time
                for employee in rule.employee_ids:
                    if employee.id == employee_id:
                        if overtime_hours >= max_overtime:
                            existing_overtime = self.env['hr.employee.overtime'].search([('month','=', month),('state','not in', ['refused','close'])])
                            ext_ovt_hours = 0.0
                            for ext_ovt in existing_overtime:
                                ext_ovt_hours = ext_ovt_hours + ext_ovt.overtime_hours
                            if  ext_ovt_hours >= max_overtime_allow:
                                pass
                            else:
                                vals = {
                                'employee_id': employee_id,
                                'date':  date,
                                'overtime_type': ovt_type,   
                                'month':  month,   
                                'check_in': check_in,
                                'check_out': check_out,
                                'total_hours': work_hours,
                                'overtime_hours': overtime_hours,
                                }
                                overtime_lines = self.env['hr.employee.overtime'].create(vals) 
                                line.update({
                                    'is_overtime': True
                                })

                

    
    
    @api.depends('check_in', 'check_out')
    def _compute_overtime_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                if delta.total_seconds() > 28800:
                    overtime_delta = delta.total_seconds() - 28800
                    attendance.overtime_hours = overtime_delta / 3600.0
                else:
                    attendance.overtime_hours = False
            else:
                attendance.overtime_hours = False
                
    
 
    

   
