from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DepartmentWise(models.TransientModel):
    _name = 'department.wise'
    _description = 'Department Wise Report'

    # location_id = fields.Many2many('hr.work.location', string='Location')
    department_ids = fields.Many2many('hr.department', string='Department')
    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    grade_type_ids = fields.Many2many('grade.type', string='Grade Type')
    location_ids = fields.Many2many('hr.location', string='Location')

    def action_generate_pdf(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'location_ids': self.location_ids.ids,
            'department_ids': self.department_ids, }
        return self.env.ref('de_hr_employee_report.action_report_department_wise').report_action(self, data=data)


    # def action_gnerate_excel(self):
    #     datas = {
    #         'date_expire': self.date_expire,
    #         'location_id': self.location_id.ids,
    #     }
    #     return self.env.ref('de_hr_employee_report.view_contract_report_xlsx').report_action(self, data=datas)