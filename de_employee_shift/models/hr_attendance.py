# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime




class HrEmployee(models.Model):
    _inherit = 'hr.attendance'

    shift_id = fields.Many2one('resource.calendar', string="Shift", help="Shift schedule", compute='_compute_employee_shift_attendance')
    shift_type_id = fields.Many2one('resource.calendar', string="Shift")
    
    @api.depends('check_in', 'check_out','employee_id')
    def _inverse_shift(self):
        for attendance in self:
            attendance.update({
                'shift_id': attendance.shift_id
            })
    
    

    @api.depends('check_in', 'check_out','employee_id')
    def _compute_employee_shift_attendance(self):
        for attendance in self:
            shift_general = self.env['resource.calendar'].search([], limit=1)
            attendance.shift_id = shift_general.id
            attendance.shift_type_id = shift_general.id
            shift_one = self.env['resource.calendar'].search([('company_id','=',attendance.employee_id.company_id.id)], limit=1)
            attendance.shift_id = shift_one.id
            attendance.shift_type_id = shift_one.id
            attendee_date = attendance.check_in.strftime('%Y-%m-%d')
            shift_contract = self.env['hr.shift.schedule.line'].search([('employee_id','=', attendance.employee_id.id),('date','=',attendee_date),('state','=','posted')], limit=1)
            if shift_contract.first_shift_id and shift_contract.second_shift_id:
                shift_one1 = 0
                shift_two1 = 0
                date_hour1 = datetime.strptime(attendee_date, '%Y-%m-%d') + relativedelta(hours =+ 0) 
                for attendee in shift_contract.first_shift_id.attendance_ids:
                    week_day = shift_contract.day.id - 1
                    if str(week_day) == attendee.dayofweek:
                        date_from = date_hour1 + relativedelta(hours =+ attendee.hour_from) - relativedelta(hours =+ 7)
                        date_to = date_hour1 + relativedelta(hours =+ attendee.hour_to) - relativedelta(hours =+ 5)
                        if str(attendance.check_in) >= str(date_from) and str(attendance.check_in) <= str(date_to):
                            shift_one1 = shift_contract.first_shift_id.id   
                            
                            
                for attendee in shift_contract.second_shift_id.attendance_ids:
                    week_day = shift_contract.day.id - 1
                    if str(week_day) == attendee.dayofweek:
                        date_from = date_hour1 + relativedelta(hours =+ attendee.hour_from) - relativedelta(hours =+ 7)
                        date_to = date_hour1 + relativedelta(hours =+ attendee.hour_to) - relativedelta(hours =+ 5)
                        
                        if str(attendance.check_in) >= str(date_from):
                            shift_two1 = shift_contract.second_shift_id.id   
                               
                            
                                                         
                        
                if shift_one1 > 0:
                    attendance.shift_id = shift_one1
                    attendance.shift_type_id = shift_one1
                    employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                    employee_active_shift.update({
                           'shift_id': shift_one1
                        })
                    
                if shift_two1 > 0:           
                    attendance.shift_id = shift_two1
                    attendance.shift_type_id = shift_two1
                    employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                    employee_active_shift.update({
                           'shift_id': shift_two1
                        })    

            elif shift_contract.first_shift_id:
                shift_one =  shift_contract.first_shift_id 
                attendance.shift_id = shift_one.id
                attendance.shift_type_id = shift_one.id
                employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                employee_active_shift.update({
                    'shift_id': shift_one.id
                        })
            
            
            elif shift_contract.second_shift_id:
                shift_two =  shift_contract.second_shift_id           
                attendance.shift_id = shift_two.id
                attendance.shift_type_id = shift_two.id
                employee_active_shift = self.env['hr.employee'].search([('id','=', attendance.employee_id.id)])
                employee_active_shift.update({
                    'shift_id': shift_two.id
                        }) 
                
     
                
    
    
    
    
    


    