# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date
from datetime import time

class AllocationShift(models.Model):
    _name = 'hr.shift.allocation'
    _description = 'This table handle the data of shift allocation in attendance'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    is_proceed = fields.Boolean(default=False)
    employee_ids = fields.Many2many('hr.employee', string="Employee", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processed', 'Process'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel')
         ],
        readonly=True, string='State', default='draft')
    week_end_days = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Permanent Off Days',copy=False,)
    shift_type_id = fields.Many2many('hr.shift', string="Permanent Shift")
    week_day_ids = fields.Many2many('shift.week.days', string="Permanent Off Days")
    allow_replicate = fields.Boolean(string="Allow Replication")

    allocation_lines = fields.One2many('hr.shift.allocation.line', 'rel_allocation')
    
    def action_cancel_shift_allocation(self):

        shift_management = self.env['hr.shift.management'].search([('date_start','=', self.date_start),('date_end','=', self.date_end)])
        for shift_mgmt in shift_management:
            shift_mgmt.update({
                'state': 'cancel'
            })
        self.update({
            'state': 'cancel'
        })    
        
                
    
    
    @api.onchange('employee_ids')
    def onchange_employees(self):
        existing_managements = self.env['hr.shift.management'].search([('date_start','>=', self.date_start),('date_start','<=', self.date_end),('date_end','<=', self.date_end),('date_end','>=', self.date_start)])
        if existing_managements: 
            for  management in existing_managements:
                existing_emp = management.employee_id.name 
                for employee in self.employee_ids:
                    for new_emp in employee:
                        if existing_emp  == new_emp.name:
                            if self.allow_replicate == True:
                                pass
                            else:    
                                raise  UserError(_(str(new_emp.name) + ' Already exist in Shift Management between ' +str(self.date_start) +' and ' + str(self.date_end) ))

        

    def unlink(self):
        if not self.env.user.has_group('de_shift_attendance.allow_parent_allocation_deletion'):
            raise UserError(('You Did Not Have Access Rights to Delete The Record '))
        else:
            super(AllocationShift,self).unlink()


  


    def action_shift_process(self):
        emp_count = 0 
        for emp in self.employee_ids:
            emp_count = emp_count + 1
        if emp_count == 0:
            raise UserError(_('Please Select Employee First!'))
            
        for line in self.allocation_lines:
            
            line.unlink()
        if self.date_start and self.date_end:
            delta = self.date_start - self.date_end
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):
                date_after_month = self.date_start + relativedelta(days=i)
                day_week = '0'
                shift_one_type = 0
                shift_two_type = 0
                shift_one = False
                shift_two = False
                rest_day = False
                if date_after_month.weekday() == 0:
                    day_week = '0'
                    for day in self.week_day_ids:
                        if day.name == 'Monday':
                            rest_day = True
                            
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            shift_two = True
                            count1 = count1 + 1
                    
                elif date_after_month.weekday() == 1:
                    day_week = '1'
                    for day in self.week_day_ids:
                        if day.name == 'Tuesday':
                            rest_day = True 
                    
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            shift_two = True
                            count1 = count1 + 1        
                        
                elif date_after_month.weekday() == 2:
                    day_week = '2'
                    for day in self.week_day_ids:
                        if day.name == 'Wednesday':
                            rest_day = True 
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   

                            shift_two = True
                            count1 = count1 + 1        
                            
                elif date_after_month.weekday() == 3:
                    day_week = '3'
                    for day in self.week_day_ids:
                        if day.name == 'Thursday':
                            rest_day = True 
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True                        
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            
                            shift_two = True
                            count1 = count1 + 1        
                            
                elif date_after_month.weekday() == 4:
                    day_week = '4'
                    for day in self.week_day_ids:
                        if day.name == 'Friday':
                            rest_day = True 
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            shift_two = True
                            count1 = count1 + 1        
                            
                elif date_after_month.weekday() == 5:
                    day_week = '5'
                    for day in self.week_day_ids:
                        if day.name == 'Saturday':
                            rest_day = True 
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            shift_two = True
                            count1 = count1 + 1        
                            
                elif date_after_month.weekday() == 6:
                    day_week = '6'
                    for day in self.week_day_ids:
                        if day.name == 'Sunday':
                            rest_day = True 
                            
                    count1 = 0       
                    for shift in self.shift_type_id: 
                        if count1 == 0:
                            shift_one_type_str = str(shift.id)
                            shift_one_type1 = shift_one_type_str.split('NewId_')
                            shift_id = ' '
                            for final_shift in shift_one_type1:
                                shift_id = shift_id + final_shift
                                
                            shift_one_type = int(shift_id)    
                            shift_one = True
                            count1 = count1 + 1
                        elif count1 == 1:
                            shift_two_type_str = str(shift.id)
                            shift_two_type1 = shift_two_type_str.split('NewId_')
                            shift_id2 = ' '
                            for final_shift in shift_two_type1:
                                shift_id2 = shift_id2 + final_shift                                
                            shift_two_type = int(shift_id2)   
                            shift_two = True
                            count1 = count1 + 1        
                
                if rest_day == True:
                    vals = {
                        'rel_allocation': self.id,
                        'date': date_after_month,
                        'day': day_week,
                        'shift_one_type': False,
                        'shift_one':False,
                        'shift_two': False,
                        'shift_two_type': False,
                        'rest_day': rest_day
                    }
                    self.env['hr.shift.allocation.line'].create(vals)
                else:
                    vals = {
                        'rel_allocation': self.id,
                        'date': date_after_month,
                        'day': day_week,
                        'shift_one_type': shift_one_type,
                        'shift_one':shift_one,
                        'shift_two': shift_two,
                        'shift_two_type': shift_two_type,
                        'rest_day': rest_day
                    }
                    self.env['hr.shift.allocation.line'].create(vals)
                    
                    i = i + 1
        self.write({
            'state': 'processed'
        })            

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.shift.allocation.sequence') or _('New')
        result = super(AllocationShift, self).create(vals)

        return result



    def action_shift_management(self):
  
        
        self.is_proceed = True
        for employee in self.employee_ids:
            line_vals = []
            for line in self.allocation_lines:
                line_vals.append((0,0, {
                    'rel_management': line.id,
                    'date': line.date,
                    'shift_one': line.shift_one_type.id,
                    'shift_two': line.shift_two_type.id,
                    'rest_day': line.rest_day,
                    'day': line.day,
                }))
            vals = {
                'employee_id': employee.id,
                'name': self.name,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'state': 'approved',
                'management_lines': line_vals
            }
            lines = self.env['hr.shift.management'].create(vals)
        self.write({
            'state': 'approved'
         })   


class AllocationShiftLine(models.Model):
    _name = 'hr.shift.allocation.line'

    rel_allocation = fields.Many2one('hr.shift.allocation')
    date = fields.Date(string='Date')
    shift_one = fields.Boolean(string='Shift 1', default=True)
    shift_one_type = fields.Many2one('hr.shift', string='Shift 1 Type')
    shift_two = fields.Boolean(string='Shift 2', default=False)
    shift_two_type = fields.Many2one('hr.shift', string='Shift 2 Type')
    # hide_field = fields.Boolean(string='Hide', default=False, readonly=True)
    rest_day = fields.Boolean(string='Rest Day')
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day',copy=False, default='0')



    # def get_day(date_string):
    #     date = datetime.strptime(date_string, '%Y-%m-%d')
    #     print('_______________________',date)
    #     return date.day


                
    @api.onchange('rest_day')
    def _onchange_rest_day(self):
        for line in self:
            if line.rest_day == True:
                line.shift_one = False
                line.shift_two = False
                line.shift_one_type = False
                line.shift_two_type = False
            else:
                line.shift_one = True
                line.shift_two = True 
                
     
    @api.onchange('shift_one')
    def onchange_shift_one(self):
        for line in self:
            if line.shift_one == True:
                line.rest_day = False
                
    @api.onchange('shift_two')
    def onchange_shift_two(self):
        for line in self:
            if line.shift_two == True:
                line.rest_day = False            
                     



    def unlink(self):
        if not self.env.user.has_group('de_shift_attendance.allow_allocation_deletion'):
            raise UserError(('You Did Not Have Access Rights to Delete The Record '))
        else:
            super(AllocationShiftLine,self).unlink()


            
class ShiftWeekdays(models.Model):
    _name = 'shift.week.days'
    _description = 'This table handle the data of shift allocation weekdays'
    
    name = fields.Char(string="Day")