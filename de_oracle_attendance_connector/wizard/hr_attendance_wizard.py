import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HrAttendanceWizard(models.TransientModel):
    _name = 'hr.attendance.wizard'
    _description = 'Attendance Wizard'

    @api.model
    def _get_all_device_ids(self):
        all_connectors = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        if all_connectors:
            return all_connectors.ids
        else:
            return []

    device_ids = fields.Many2many('oracle.setting.connector', string='Connector', default=_get_all_device_ids, domain=[('state', '=', 'active')])
    
    
   
    def cron_download_oracle_attendance(self):
        devices = self.env['oracle.setting.connector'].search([('state', '=', 'active')])
        for device in devices:
            device.action_get_attendance_data()
        
        
    def cron_hr_user_attendance_validate(self):
        user_attendance = self.env['hr.user.attendance']
        user_attendance.action_attendace_validated()
        
   

