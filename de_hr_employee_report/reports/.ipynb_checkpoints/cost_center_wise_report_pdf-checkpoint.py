# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class CostCenterWisePDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.cost_centerwise_pdf'
    _description = 'Cost Center Wise PDF Report'

    def _get_report_values(self, docids, data):

        type_employee = self.env['employee.type'].search([('id', 'in', data['employee_type_ids'])]).ids
        type_grade = self.env['grade.type'].search([('id', 'in', data['grade_type_ids'])]).ids
        cost_center = self.env['account.analytic.account'].search([('id', 'in', data['cost_center_ids'])]).ids
        location_ids = self.env['hr.location'].search([('id','in',data['location_ids'])]).ids

        active_contract = self.env['hr.contract'].search(['|', ('state', '=', 'open'),
                                                          ('employee_id.emp_type', 'in', type_employee),
                                                          ('employee_id.grade_type', 'in', type_grade),
                                                          ('employee_id.hr_location_id', 'in',location_ids),
                                                          ('cost_center_information_line.cost_center', 'in',
                                                           cost_center)])
        print(active_contract)
        return {
            'doc_ids': self.ids,
            'doc_model': 'cost.center.wise',
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
