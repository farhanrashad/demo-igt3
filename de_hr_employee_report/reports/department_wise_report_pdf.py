# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class DepartmentWisePDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.department_wise_pdf'
    _description = 'Department Wise PDF Report'

    def _get_report_values(self, docids, data):
        type_employee = self.env['employee.type'].search([('id', 'in', data['employee_type_ids'])])
        employee_type = []
        for rec in type_employee:
            employee_type.append(rec.name)
        type_grade = self.env['grade.type'].search([('id', 'in', data['grade_type_ids'])]).ids
        location_ids = self.env['hr.location'].search([('id', 'in', data['location_ids'])]).ids
        emp_dept_ids = self.env['hr.department'].search([('id', 'in', data['location_ids'])]).ids
        if not type_employee and not type_grade and not location_ids and not emp_dept_ids:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open')])
        elif type_employee and type_grade and location_ids and emp_dept_ids:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', type_grade),
                                                              ('employee_id.hr_location_id', 'in', location_ids),
                                                              ('employee_id.department_id', 'in', emp_dept_ids),
                                                              ])
        elif type_employee and type_grade and location_ids:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', type_grade),
                                                              ('employee_id.hr_location_id', 'in', location_ids),
                                                              ])

        return {
            'doc_ids': self.ids,
            'doc_model': 'department.wise',
            # 'data': data,
            # 'location': location_extract,
            # 'active_contract': active_contract,
        }

        # # location = self.env['hr.work.location'].search([('id', '=', data['location_ids'])])
        # location = self.env['hr.location'].search([('id', '=', data['location_ids'])])
        # location_extract = ''
        # for loc in location:
        #     location_extract = location_extract + loc.name + ','
        # if location:
        #     active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
        #                                                       ('date_end', '<', data['date_expire']),
        #                                                       ('employee_id.hr_location_id', 'in',
        #                                                        data['location_ids'])], order='date_end asc')
        # else:
        #     active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
        #                                                       ('date_end', '<', data['date_expire'])], order='date_end asc')
