from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class UserAttendance(models.Model):
    _name = 'user.attendance'
    _description = 'User Attendance'
    _order = 'timestamp DESC, user_id, status, attendance_state_id, device_id'

    device_id = fields.Many2one('attendance.device', string='Attendance Device', required=True, ondelete='restrict', index=True)
    user_id = fields.Many2one('attendance.device.user', string='Device User', required=True, ondelete='cascade', index=True)
    timestamp = fields.Datetime(string='Timestamp', required=True, index=True)
    status = fields.Integer(string='Device Attendance State', required=True,
                            help='The state which is the unique number stored in the device to'
                            ' indicate type of attendance (e.g. 0: Checkin, 1: Checkout, etc)')
    attendance_state_id = fields.Many2one('attendance.state', string='Odoo Attendance State',
                                          help='This technical field is to map the attendance'
                                          ' status stored in the device and the attendance status in Odoo', required=True, index=True)
    activity_id = fields.Many2one('attendance.activity', related='attendance_state_id.activity_id', store=True, index=True)
    hr_attendance_id = fields.Many2one('hr.attendance', string='HR Attendance', ondelete='set null',
                                       help='The technical field to link Device Attendance Data with Odoo\' Attendance Data', index=True)

    type = fields.Selection([('checkin', 'Check-in'),
                            ('checkout', 'Check-out')], string='Activity Type', related='attendance_state_id.type', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id', store=True, index=True)
    valid = fields.Boolean(string='Valid Attendance', index=True, readonly=True, default=False,
                           help="This field is to indicate if this attendance record is valid for HR Attendance Synchronization."
                           " E.g. The Attendances with Check out prior to Check in or the Attendances for users without employee"
                           " mapped will not be valid.")
    is_attedance_created = fields.Boolean(string="Is Attendance")

    _sql_constraints = [
        ('unique_user_id_device_id_timestamp',
         'UNIQUE(user_id, device_id, timestamp)',
         "The Timestamp and User must be unique per Device"),
    ]

    @api.constrains('status', 'attendance_state_id')
    def constrains_status_attendance_state_id(self):
        for r in self:
            if r.status != r.attendance_state_id.code:
                raise(_('Attendance Status conflict! The status number from device must match the attendance status defined in Odoo.'))

    def is_valid(self):
        self.ensure_one()
        if not self.employee_id:
            return False

        prev_att = self.search([('employee_id', '=', self.employee_id.id),
                                ('timestamp', '<', self.timestamp),
                                ('activity_id', '=', self.activity_id.id)], limit=1, order='timestamp DESC')
        if not prev_att:
            valid = self.type == 'checkin' and True or False
        else:
            valid = prev_att.type != self.attendance_state_id.type and True or False
        return False

    @api.model_create_multi
    def create(self, vals_list):
        attendances = super(UserAttendance, self).create(vals_list)
        valid_attendances = attendances.filtered(lambda att: att.is_valid())
        if valid_attendances:
            valid_attendances.write({'valid': True})
        return attendances

    def action_attendace_validated(self):
        month_datetime = fields.date.today() - timedelta(32)
        for month_date in range(32):
            datetime =  month_datetime + timedelta(month_date)
            date_start = datetime + relativedelta(hours =+ 0)
            date_end = datetime + relativedelta(hours =+ 23.99)
            total_employee = self.env['hr.employee'].search([])
            for employee in total_employee:
                attendance_test = self.env['user.attendance']
                count = attendance_test.search_count([('employee_id','=',employee.id)])
                shift_management = self.env['hr.shift.management'].search([('employee_id','=',employee.id),('state','=','approved')])
                first_shift_type = 0
                second_shift_type = 0
                for multishift in shift_management:
                    for shift_line in multishift.management_lines:
                        if   str(shift_line.date) == str(datetime):
                            first_shift_type = shift_line.shift_one.id    
                            second_shift_type = shift_line.shift_two.id 

                first_shift = self.env['hr.shift'].search([('id','=', first_shift_type)])  
                second_shift = self.env['hr.shift'].search([('id','=', second_shift_type)])
                
                
               
                if first_shift and second_shift:
                    shift1_attendance_checkin = attendance_test.search([('employee_id','=',employee.id),('timestamp','>=',date_start),('timestamp','<=',date_end),('is_attedance_created','=',False)], order="timestamp asc", limit=1)
                    shift1_attendance_checkout = attendance_test.search([('employee_id','=',employee.id),('timestamp','>=',date_start),('timestamp','<=',date_end),('is_attedance_created','=',False)], order="timestamp desc", limit=2)
#                         for
                    if shift1_attendance_checkin:
                        vals = {
                                'employee_id': shift1_attendance_checkin.employee_id.id,
                                'check_in': shift1_attendance_checkin.timestamp,
                                'shift_type_id' : first_shift.id if first_shift else False ,
                                'shift_time_in' : first_shift.time_in if first_shift else False ,
                                'shift_time_out' : first_shift.time_out if first_shift else False , 
                                }
                        hr_attendance = self.env['hr.attendance'].create(vals)

                        shift1_attendance_checkin.update({
                            'is_attedance_created' : True
                        })
                    if shift1_attendance_checkout:
                        shift2_attendee_count = 0
                        
                        datedual_shift = shift1_attendance_checkout[0].timestamp.strftime('%Y-%m-%d')
                        partner =  shift1_attendance_checkout[0].employee_id.id
                        existing_attendance_shift1 = self.env['hr.attendance'].search([('employee_id','=',partner),('check_in','<=', shift1_attendance_checkout[0].timestamp), ('check_out','=', False)], order="check_in asc", limit=1)
                        
#                         raise UserError(_(str(existing_attendance_shift1.id) + str(datedual_shift) + str(partner) + str(datedual_shift)))
                        
                        for shift1attendee in shift1_attendance_checkout:
                            shift2_attendee_count = shift2_attendee_count + 1
                        if shift2_attendee_count == 2:
                            existing_attendance_shift1.update({
                                'check_out': shift1_attendance_checkout[1].timestamp
                            }) 
                            shift1_attendance_checkout[1].update({
                                   'is_attedance_created' : True
                            })
                        
                            vals = {
                                'employee_id': shift1_attendance_checkout[0].employee_id.id,
                                'check_in': shift1_attendance_checkout[0].timestamp,
                                'shift_type_id' : second_shift.id if second_shift else False ,
                                'shift_time_in' : second_shift.time_in if second_shift else False ,
                                'shift_time_out' : second_shift.time_out if second_shift else False , 

                                    }
                            hr_attendance = self.env['hr.attendance'].create(vals)

                            shift1_attendance_checkout[0].update({
                                'is_attedance_created' : True
                            })
                        
                    shift1_attendance_list = attendance_test.search([('employee_id','=',employee.id),('timestamp','>=',date_start),('timestamp','<=',date_end),('is_attedance_created','=',False)], order="timestamp asc",) 
                    for shift1attendee_list in  shift1_attendance_list:
                        shift1attendee_list.update({
                                    'is_attedance_created' : True
                                })    
                        
                        
                    
                    
                                
                else:
                    attendance_list = attendance_test.search([('employee_id','=',employee.id),('timestamp','>=',date_start),('timestamp','<=',date_end),('is_attedance_created','=',False)], order="timestamp asc",)

                    if attendance_list:
                        count = 0
                        
                        for attendace in attendance_list:
                            existing_attendance = self.env['hr.attendance'].search([('employee_id','=',attendace.employee_id.id),('check_in','<=', attendace.timestamp), ('check_out','=', False)], order="check_in desc", limit=1)
                            datetime2 =  attendace.timestamp - timedelta(1)
                            datetime21 = datetime2.strftime('%Y-%m-%d')
                            existing_attendance2 = self.env['hr.attendance'].search([('employee_id','=',attendace.employee_id.id),('shift_type_id.shift_type','=', 'night'), ('check_out','=', False) ]) 
    #                         raise UserError('User'+ str(existing_attendance2.id))
                            for uniq_attendance in existing_attendance2:
                                emp_date = uniq_attendance.check_in.strftime('%Y-%m-%d')


                                if str(datetime21) == str(emp_date): 
    #                                 pass 
    #                                 raise UserError('User'+ str(existing_attendance2.id))
                                    if uniq_attendance.shift_type_id.shift_type == 'night':
                                        uniq_attendance.update({
                                            'check_out': attendace.timestamp,
                                        })
                                        attendace.update({
                                        'is_attedance_created' : True
                                        })


                            if existing_attendance: 
    #                            raise UserError (_(''+ str(existing_attendance.check_in.strftime('%Y-%m-%d')) + str(attendace.timestamp.strftime('%Y-%m-%d'))))
                               if  str(existing_attendance.check_in.strftime('%Y-%m-%d'))  == str(attendace.timestamp.strftime('%Y-%m-%d')): 
    #                             raise UserError('User'+ str(existing_attendance.id))

                                    existing_attendance.update({
                                      'check_out': attendace.timestamp,
                                    })
                                    attendace.update({
                                        'is_attedance_created' : True
                                    })
                               else:
                                    if  count >= 1 and second_shift:
                                        vals = {
                                         'employee_id': attendace.employee_id.id,
                                         'check_in': attendace.timestamp,
                                         'shift_type_id' : second_shift.id if second_shift else False ,
                                         'shift_time_in' : second_shift.time_in if second_shift else False ,
                                         'shift_time_out' : second_shift.time_out if second_shift else False , 
                                         }
                                        hr_attendance = self.env['hr.attendance'].create(vals)
                                        attendace.update({
                                        'is_attedance_created' : True
                                        })

                                    else:
                                        if attendace.is_attedance_created == False:
                                            vals = {
                                            'employee_id': attendace.employee_id.id,
                                            'check_in': attendace.timestamp,
                                            'shift_type_id' : first_shift.id if first_shift else False ,
                                            'shift_time_in' : first_shift.time_in if first_shift else False ,
                                            'shift_time_out' : first_shift.time_out if first_shift else False , 
                                            }
                                            hr_attendance = self.env['hr.attendance'].create(vals)
                                            attendace.update({
                                            'is_attedance_created' : True
                                            })
                                            count = count + 1



                            if not existing_attendance:
                                if  count >= 1 and second_shift:
                                    vals = {
                                     'employee_id': attendace.employee_id.id,
                                     'check_in': attendace.timestamp,
                                     'shift_type_id' : second_shift.id if second_shift else False ,
                                     'shift_time_in' : second_shift.time_in if second_shift else False ,
                                     'shift_time_out' : second_shift.time_out if second_shift else False , 
                                     }
                                    hr_attendance = self.env['hr.attendance'].create(vals)
                                    attendace.update({
                                        'is_attedance_created' : True
                                    })

                                else:

                                    vals = {
                                        'employee_id': attendace.employee_id.id,
                                        'check_in': attendace.timestamp,
                                        'shift_type_id' : first_shift.id if first_shift else False ,
                                        'shift_time_in' : first_shift.time_in if first_shift else False ,
                                        'shift_time_out' : first_shift.time_out if first_shift else False , 
                                        }
                                    hr_attendance = self.env['hr.attendance'].create(vals)
                                    count = count + 1

                                    attendace.update({
                                        'is_attedance_created' : True
                                    })
                                
                        
        
                    
                    




  
