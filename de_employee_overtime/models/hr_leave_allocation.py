# -*- coding: utf-8 -*-

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    
    number_of_hours_calc = fields.Float(
        'Duration (hours)',
        help="If Accrual Allocation: Number of hours allocated in addition to the ones you will get via the accrual' system.")
   
    
    @api.depends('number_of_days', 'employee_id')
    def _compute_number_of_hours_display(self):
        for allocation in self:
            if allocation.parent_id and allocation.parent_id.type_request_unit == "hour":
                allocation.number_of_hours_display = allocation.number_of_days * HOURS_PER_DAY
            elif allocation.number_of_days:
                allocation.number_of_hours_display = allocation.number_of_days * (allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day or HOURS_PER_DAY)
            else:
                allocation.number_of_hours_display = 0.0
                
            if allocation.number_of_hours_calc > 0.0:
                allocation.number_of_hours_display = allocation.number_of_hours_calc    
                
   
