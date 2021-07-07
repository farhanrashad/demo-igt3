import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class OvertimeWizard(models.TransientModel):
    _name = 'overtime.wizard'
    _description = 'Overtime Wizard'

       
        
    def cron_create_employee_overtime(self):
        user_attendance = self.env['hr.shift.attendance']
        user_attendance.action_employee_overtime()    
        


    
