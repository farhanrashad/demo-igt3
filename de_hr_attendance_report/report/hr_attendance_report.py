# -*- coding: utf-8 -*-

import time
from odoo import api, models, _ , fields 
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class PurchaseAttendanceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report.attendance_report'
    _description = 'Hr Attendance Report'

    
    
    
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employees_attendance = []
        
        for employee in docs.employee_ids:
            work_day_line = []    
            employee1 = self.env['hr.employee'].search([('id',
                                                       '=', employee.id)], limit=1)
            date_from = docs.start_date
            date_to = docs.end_date

            work_days = 0
            work_hours = 0 
            
            """
              Employee Attendance Days
            """ 
            emp_attendance = self.env['hr.attendance'].search([('employee_id','=', employee1.id),('check_in','>=', date_from),('check_out','<=', date_to),('company_id','=',employee1.company_id.id)])
            previous_date = fields.date.today()
            work_entry_type = self.env['hr.work.entry.type'].search([('code','=','WORK100')], limit=1)
            for attendance in emp_attendance:
                if attendance.check_out:
                    new_date = attendance.check_out.strftime('%y-%m-%d')
                    if new_date != previous_date:
                       work_days += 1
                       work_hours += attendance.worked_hours 
                    previous_date = attendance.check_out.strftime('%y-%m-%d')
            work_day_line.append({
               'work_entry_type_id' : work_entry_type.id ,
               'name': work_entry_type.name ,
               'sequence': work_entry_type.sequence ,
               'number_of_days' : work_days ,
               'number_of_hours' : work_hours ,
            })
                      
            """
              Employee Timoff by Timeoff type wise
            """ 
            
            leave_type = []
            
            total_leave_days = 0
            emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee1.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','=','validate')])
            previous_date = fields.date.today()
            leave_work_entry_type = self.env['hr.work.entry.type'].search([('code','=','LEAVE100')], limit=1)
            for leave in emp_leaves: 
                leave_type.append(leave.holiday_status_id.id)
            uniq_leave_type = set(leave_type)
            for timeoff_type in uniq_leave_type:
                leave_work_days = 0
                leaves_work_hours = 0 
                emp_leaves_type = self.env['hr.leave'].search([('holiday_status_id','=', timeoff_type),('employee_id','=', employee1.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','=','validate')])
                for timeoff in emp_leaves_type:
                    leave_work_days += timeoff.number_of_days
                    total_leave_days += timeoff.number_of_days 
                timeoff_vals = self.env['hr.leave.type'].search([('id','=',timeoff_type)], limit=1) 
                
                timeoff_work_entry_type = self.env['hr.work.entry.type'].search([('code','=',timeoff_vals.name)], limit=1)
                if not timeoff_work_entry_type:
                    vals = {
                        'name': timeoff_vals.name,
                        'code': timeoff_vals.name,
                        'round_days': 'NO',
                    }
                    work_entry = self.env['hr.work.entry.type'].create(vals)
                timeoff_work_entry_type = self.env['hr.work.entry.type'].search([('code','=',timeoff_vals.name)], limit=1)

                work_day_line.append({
                   'work_entry_type_id' : timeoff_work_entry_type.id,
                   'name': timeoff_work_entry_type.name,
                   'sequence': timeoff_work_entry_type.sequence,
                   'number_of_days' : leave_work_days,
                   'number_of_hours' : leave_work_days * employee1.shift_id.hours_per_day ,
                })               
                
            """
              Employee Absent Days
            """ 
            absent_work_days_initial = 0
            delta = docs.start_date - docs.end_date
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):
                absent_work_days_initial = absent_work_days_initial + 1    
            rest_days_initial = 0
            absent_work_days = 0
            shift_contract_lines = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee1.id),('date','>=',date_from),('date','<=',date_to),('state','=','posted')])
            for shift_line in shift_contract_lines:
                if shift_line.rest_day != True:
                    rest_days_initial = rest_days_initial + 1 
                    
            absent_work_entry_type = self.env['hr.work.entry.type'].search([('code','=','ABSENT100')], limit=1)
            if not absent_work_entry_type:
                vals = {
                    'name': 'Absent Days',
                    'code': 'ABSENT100',
                    'round_days': 'NO',
                }
                work_entry = self.env['hr.work.entry.type'].create(vals)
            apply_leave_days = 0    
            emp_leaves_apply = self.env['hr.leave'].search([('employee_id','=', employee1.id),('date_from','>=', date_from),('date_to','<=', date_to),('state','=','validate')]) 
            for leave_apply in emp_leaves_apply:
                apply_leave_days += leave_apply.number_of_days
            
            absent_work_days = absent_work_days_initial - (total_leave_days + work_days)
            absent_work_entry_type = self.env['hr.work.entry.type'].search([('code','=','ABSENT100')], limit=1)
            
            work_day_line.append({
               'work_entry_type_id' : absent_work_entry_type.id,
               'name': absent_work_entry_type.name,
               'sequence': absent_work_entry_type.sequence,
               'number_of_days' : absent_work_days ,
               'number_of_hours' : absent_work_days * employee1.shift_id.hours_per_day ,
            })
            


    
            attendances = []
            delta = docs.start_date - docs.end_date
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):            
                day = ' '
                remarks = ' '
                rest_day = 'N'                    

                date_after_month = docs.start_date + relativedelta(days=i)

                hr_attendance = self.env['hr.attendance'].search([('employee_id','=', employee.id),('att_date','=', date_after_month)]) 
                if hr_attendance:
                    for attendance in hr_attendance:

                        emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                        shift = attendance.shift_id.name
                        current_shift = attendance.shift_id
                        if  attendance.check_out and attendance.check_in:
                            remarks = 'Attendance Present.'
                        elif not attendance.check_out and attendance.check_in:
                            remarks = 'Check Out is Missing' 
                        elif not attendance.check_in and attendance.check_out: 
                            remarks = 'Check In is Missing'
                        elif emp_leaves:
                            remarks = str(emp_leaves.holiday_status_id.name)
                        else:
                            remarks = 'Absent.'
                        if not  shift:   
                            shift = self.env['resource.calendar'].search([], limit=1).name
                            shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                            current_shift = self.env['resource.calendar'].search([], limit=1)
                            current_shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1)
                            shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                            if shift_line.first_shift_id:
                                shift = shift_line.first_shift_id.name
                                current_shift = attendance.shift_id
                            elif shift_line.second_shift_id:
                                shift = shift_line.second_shift_id.name
                                current_shift = attendance.shift_id

                        rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                        if rest_schedule_line:
                            rest_day = 'Y'    
                            remarks = 'Restday.'

                        request_date = date_after_month + relativedelta(hours =+ 4)    
                        for gazetted_day in current_shift.global_leave_ids:
                            if str(request_date) >= str(gazetted_day.date_from) and str(request_date) <= str(gazetted_day.date_to):
                                remarks = str(gazetted_day.name) 


                        day1 = date_after_month.strftime('%A')    

                        check_in_time =  attendance.check_in
                        check_out_time = attendance.check_out
                        if  attendance.check_in:
                            check_in_time = attendance.check_in + relativedelta(hours =+ 5)

                        if  attendance.check_out:
                            check_out_time = attendance.check_out + relativedelta(hours =+ 5)

                        attendances.append({
                            'date': date_after_month,
                            'day':  day1,
                            'check_in': check_in_time,
                            'check_out':  check_out_time,
                            'hours': attendance.worked_hours,
                            'shift': shift,
                            'rest_day': rest_day,
                            'remarks': remarks,
                        })
                else:
                    emp_leaves = self.env['hr.leave'].search([('employee_id','=', employee.id),('request_date_from','=', date_after_month)], limit=1)
                    if emp_leaves:
                        remarks = str(emp_leaves.holiday_status_id.name)
                    else:
                        remarks = 'Absent.'

                    shift = self.env['resource.calendar'].search([], limit=1).name
                    shift = self.env['resource.calendar'].search([('company_id','=', employee.company_id.id)], limit=1).name
                    shift_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month)], limit=1)
                    if shift_line.first_shift_id:
                        shift = shift_line.first_shift_id.name
                    elif shift_line.second_shift_id:
                        shift = shift_line.second_shift_id.name                    

                    rest_schedule_line = self.env['hr.shift.schedule.line'].search([('employee_id','=', employee.id),('date','=', date_after_month),('rest_day','=', True)], limit=1)

                    if rest_schedule_line:
                        rest_day = 'Y'    
                        remarks = 'Restday.'

                    day1 = date_after_month.strftime('%A')    

                    check_in_time =  ' '
                    check_out_time = ' '

                    attendances.append({
                        'date': date_after_month,
                        'day':  day1,
                        'check_in': check_in_time,
                        'check_out':  check_out_time,
                        'hours': 0.0,
                        'shift': shift,
                        'rest_day': rest_day,
                        'remarks': remarks,
                    })
                    
            employees_attendance.append({
                'name': employee.name,
                'workdays': work_day_line,
                'employee_no': employee.emp_number,
                'attendances': attendances,
            })        
        return {
                'employee': docs,
                'employees_attendance': employees_attendance,
               }
        