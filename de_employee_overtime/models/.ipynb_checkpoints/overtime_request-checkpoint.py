# -*- coding: utf-8 -*-

from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
import math



class HrOverTime(models.Model):
    _name = 'hr.overtime.request'
    _description = "HR Overtime Request"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    
    
    def action_submit(self):
        for line in self:
            if line.state == 'draft':
                line.update({
                    'state': 'to_approve'
                })
        
    def action_cancel(self):
        for line in self:
            if line.state not in ['approved', 'paid']:
                line.update({
                    'state': 'close'
                }) 
            
    def unlink(self):
        for ovt in self:
            if ovt.state not in ('draft','close'):
                raise UserError(_('You cannot delete an Document  which is not draft or cancelled. '))
     
            return super(HrOverTime, self).unlink()  
    
    
    def generate_normal_overtime_compansation(self):
        """
         Generate Overtime Entries 
         1- By Normal Overtime type
        """
        for line in self:
            ot_amount = 0.0
            nrate = 0
            for compansation in line.overtime_type_id.type_line_ids:
                if line.overtime_hours >= compansation.ot_hours:
                    if compansation.compansation == 'payroll':
                        if compansation.rate_type == 'fix_amount':
                            ot_amount = compansation.rate * line.overtime_hours 
                        elif compansation.rate_type == 'percent':
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1)   
                            ot_hour_amount = (contract.wage * compansation.rate_percent ) /(compansation.hours_per_day * compansation.month_day)
                            nrate = compansation.rate_percent
                            ot_amount = ot_hour_amount * line.overtime_hours
            total_amount = ot_amount
            if  line.overtime_type_id.type == 'normal': 
                if total_amount > 0:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                            'amount': total_amount ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': line.overtime_hours,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+ str(nrate)
                    }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
                


                
    def generate_overtime_compansation(self):
        """
         Generate Overtime Entries 
         1- By Using Overtime type
        """
        for line in self:
            gazetted_hours = 0
            leave_period = ' '
            leave_type = 0
            only_cpl = False
            singl_hours = 0.0 
            single_ot_amount = 0.0
            double_ot_amount = 0.0
            grate = 0
            grate2 = 0
            double_rate_ot_hours = 0.0 
            single_hour_limit = 0.0 
            only_cpl = line.employee_id.cpl
            for compansation in line.overtime_type_id.type_line_ids:
                if line.hours >= compansation.ot_hours:
                    if compansation.compansation == 'leave':
                        gazetted_hours = line.hours 
                        if leave_period != 'full_day':
                            leave_type = compansation.leave_type_id.id     
                            leave_period = compansation.leave_type  
                    elif compansation.compansation == 'payroll':
                        if compansation.rate_type == 'fix_amount':
                            ot_amount = compansation.rate * line.overtime_hours 
                            grate =  compansation.rate
                        elif compansation.rate_type == 'percent' and compansation.entry_type_id == 'single' and singl_hours < compansation.ot_hours:
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1) 
                            single_ot_hour_amount = (contract.wage * compansation.rate_percent ) /(compansation.hours_per_day * compansation.month_day)             
                                    
                            grate =  compansation.rate_percent
                            double_hours_limit = 0.0
                            singl_hours = line.hours
                            for compansation1 in line.overtime_type_id.type_line_ids:
                                if line.hours >= compansation1.ot_hours:
                                    if compansation1.rate_type == 'percent' and compansation1.entry_type_id == 'double' and double_hours_limit < compansation1.ot_hours:
                                        double_hours_limit =  compansation1.ot_hours
                            single_hour_limit1  =   line.hours - singl_hours            
                            single_hour_limit = line.hours - single_hour_limit1
                            
                            single_ot_amount = single_ot_hour_amount * single_hour_limit
                                    
                                    
                                    
                        elif compansation.rate_type == 'percent' and compansation.entry_type_id == 'double' and double_rate_ot_hours < compansation.ot_hours:
                                    
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1)
                            double_ot_hour_amount = (contract.wage * compansation.rate_percent ) /(compansation.hours_per_day * compansation.month_day)  
                            grate2 =  compansation.rate_percent

                            double_rate_ot_hours = 0
                            single_rate_ot_hours = 0.0
                            single_hourss_limit  = 0.0
                            for compansationin in line.overtime_type_id.type_line_ids:
                                if compansationin.rate_type == 'percent' and compansationin.entry_type_id == 'single' and single_hourss_limit < compansationin.ot_hours:
                                    single_hourss_limit =  compansationin.ot_hours
                            double_rate_ot_hours =   line.hours - single_hourss_limit                                   
                            double_ot_amount = double_ot_hour_amount * double_rate_ot_hours
            if single_ot_amount > 0:
                if only_cpl == False:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                            'amount': round(single_ot_amount) ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': single_hour_limit,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+str(grate)                                    
                                          }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
            if double_ot_amount > 0:
                if only_cpl == False:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                            'amount': round(double_ot_amount) ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': double_rate_ot_hours,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+str(grate2) ,
                                            }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
            if leave_type > 0:
                leave_total_hours = 0
                if leave_period == 'half_day':
                    leave_total_hours = 4
                elif leave_period == 'full_day':
                    leave_total_hours = line.employee_id.shift_id.hours_per_day 
                if leave_total_hours > 0:    
                    vals = {
                        'holiday_status_id': leave_type,
                        'employee_id': line.employee_id.id,            
                        'holiday_type': 'employee',
                        'allocation_type': 'regular',
                        'number_of_hours_calc': leave_total_hours,
                        'name':  "Timeoff  Allocation Created From Employee Overtime Compansation Type "+str(line.overtime_type_id.name), 

                                }
                    timeoff = self.env['hr.leave.allocation'].create(vals)
                        
                    timeoff.action_approve()                        
                            
                
                
      
    
    
    
    def generate_rest_days_overtime_compansation(self):
        for line in self:
            leave_period = ' '
            leave_type = 0
            only_cpl = False
            rate = 0
            rest_singl_hours = 0.0 
            rest_single_ot_amount = 0.0
            rest_double_ot_amount = 0.0
            rest_double_rate_ot_hours = 0.0 
            rest_single_hour_limit = 0.0 
            for rest_compansation in line.overtime_type_id.type_line_ids:
                only_cpl = rest_compansation.employee_id.cpl
                if line.hours >= rest_compansation.ot_hours:
                    if rest_compansation.compansation == 'leave':
                        rest_hours = line.hours 
                        if leave_period != 'full_day':
                            leave_type = rest_compansation.leave_type_id.id     
                            leave_period = rest_compansation.leave_type  
                    elif rest_compansation.compansation == 'payroll':
                        if rest_compansation.rate_type == 'fix_amount':
                            ot_amount = rest_compansation.rate * line.overtime_hours 
                            rate = rest_compansation.rate
                        elif rest_compansation.rate_type == 'percent' and rest_compansation.entry_type_id == 'single' and rest_singl_hours < rest_compansation.ot_hours:
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1) 
                            rest_single_ot_hour_amount = (contract.wage * rest_compansation.rate_percent ) /(rest_compansation.hours_per_day * rest_compansation.month_day)
                            rate = rest_compansation.rate_percent
                            rest_double_hours_limit = 0.0
                            rest_singl_hours = line.hours
                            for compansation1rest in line.overtime_type_id.type_line_ids:
                                if line.hours >= compansation1rest.ot_hours:
                                    if compansation1rest.rate_type == 'percent' and compansation1rest.entry_type_id == 'double' and rest_double_hours_limit < compansation1rest.ot_hours:
                                        rest_double_hours_limit =  compansation1.ot_hours

                            rest_single_hour_limit1  =   line.hours - rest_singl_hours            
                            rest_single_hour_limit = line.hours - rest_single_hour_limit1
                                    
                            rest_single_ot_amount = rest_single_ot_hour_amount * rest_single_hour_limit
                                    
                                    
                                    
                        elif rest_compansation.rate_type == 'percent' and rest_compansation.entry_type_id == 'double' and rest_double_rate_ot_hours < rest_compansation.ot_hours:
                                    
                            contract = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id),('state','=','open')], limit=1)
                            rest_double_ot_hour_amount = (contract.wage * rest_compansation.rate_percent ) /(rest_compansation.hours_per_day * rest_compansation.month_day)  
                            rate = rest_compansation.rate_percent
                            rest_double_rate_ot_hours = 0
                            rest_single_rate_ot_hours = 0.0
                            rest_single_hourss_limit  = 0.0
                            leave_period_rest = ' '
                            for compansationinrest in line.overtime_type_id.type_line_ids:
                                if compansationinrest.rate_type == 'percent' and compansationinrest.entry_type_id == 'single' and rest_single_hourss_limit < compansationinrest.ot_hours:
                                    rest_single_hourss_limit =  compansationinrest.ot_hours
                                    raise UserError(('test '+str(compansationinrest.ot_hours))) 
                                if compansationinrest.compansation == 'leave': 
                                    leave_period_rest = compansationinrest.leave_type
                                    rest_single_hourss_limit =  compansationinrest.ot_hours     
                            rest_double_rate_ot_hours =   line.hours - rest_single_hourss_limit
                            rest_double_ot_amount = rest_double_ot_hour_amount * rest_double_rate_ot_hours
                                    
            if rest_single_ot_amount > 0:
                if only_cpl == False:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                            'amount': round(rest_single_ot_amount) ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': rest_single_hour_limit,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+str(rate),
                            }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
                
            if rest_double_ot_amount > 0:
                if only_cpl == False:
                    entry_vals = {
                            'employee_id': line.employee_id.id,
                            'date': line.date,
                             'amount': round(rest_double_ot_amount) ,
                            'company_id':  line.company_id.id,
                            'overtime_hours': rest_double_rate_ot_hours,
                            'overtime_type_id': line.overtime_type_id.id,
                            'remarks': '@rate '+ str(rate),
                            }
                    overtime_entry = self.env['hr.overtime.entry'].create(entry_vals)
                
            if leave_type > 0:
                leave_total_hours = 0
                if leave_period == 'half_day':
                    leave_total_hours = 4
                elif leave_period == 'full_day':
                    leave_total_hours = line.employee_id.shift_id.hours_per_day 
                if leave_total_hours > 0:    
                    vals = {
                        'holiday_status_id': leave_type,
                        'employee_id': line.employee_id.id,            
                        'holiday_type': 'employee',
                        'allocation_type': 'regular',
                        'number_of_hours_calc': leave_total_hours,
                        'name':  "Timeoff  Allocation Created From Employee Overtime Compansation Type "+str(line.overtime_type_id.name), 

                                }
                    timeoff = self.env['hr.leave.allocation'].create(vals)
                        
                    timeoff.action_approve() 
            
            
            
            
                    
                        
    def action_approve(self):
        for line in self:
            if line.state == 'to_approve':
                ot_amount = 0
                gazetted_hours = 0
                nrate = 0
                leave_period = ' '
                leave_type = 0
                if line.overtime_type_id.type == 'normal':
                    line.generate_normal_overtime_compansation() 
                    
                elif line.overtime_type_id.type == 'rest_day':
                    line.generate_rest_days_overtime_compansation() 
                                                    
                elif  line.overtime_type_id.type == 'gazetted': 
                    line.generate_overtime_compansation() 
    
                line.update({
                        'state': 'approved'
                        })     
                
                
    
    def action_refuse(self):
        for line in self:
            line.update({
                'state': 'refused'
            })
     
    
    employee_id = fields.Many2one('hr.employee', string="Name")
    date_from = fields.Datetime('Date From', required=True)
    company_id = fields.Many2one('res.company', string="Company")
    date = fields.Date('Date', required=True)
    date_to = fields.Datetime('Date to', required=True)
    overtime_type_id = fields.Many2one('hr.overtime.type', string="Overtime Type", domain="['|',('company_id','=',company_id), ('company_id','=',False)]")
    hours = fields.Float('Total Hours')
    overtime_hours = fields.Float('Feeded Hours')
    actual_ovt_hours = fields.Float('Actual Overtime Hours', readonly=True, )
    attendance_ids = fields.Many2many('hr.attendance', string="Attendance")
    remarks = fields.Char(string="Remarks")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),        
        ('paid', 'Paid'),
        ('close', 'Cancelled'),
        ('refused', 'Refused')], string="Status",
                             default="draft")
    
    @api.constrains('overtime_hours')
    def _check_leave_type(self):
        for line in self:
            if line.overtime_hours:
                if line.overtime_hours > line.actual_ovt_hours:
                    line.overtime_hours = line.actual_ovt_hours

    
    


    @api.depends('hours')
    def _get_overtime_hours(self):
        for ovt in self:
            overtime_hours = ovt.hours - ovt.employee_id.shift_id.hours_per_day    
            ovt.actual_ovt_hours = overtime_hours
            
    @api.depends('date_from', 'date_to')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'hours': hours ,
                })

    