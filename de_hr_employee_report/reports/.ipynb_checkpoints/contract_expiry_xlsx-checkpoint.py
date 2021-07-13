import xlwt
from odoo import models
from datetime import datetime, date
from odoo.exceptions import UserError


class ContractExpiryReport(models.AbstractModel):
    _name = 'report.de_hr_employee_report.contract_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # workbook.add_worksheet('Partner Ledger')
        format1 = workbook.add_format({'font_size': '14', 'align': 'vcenter', 'bold': True})
        width = 4
        sheet = workbook.add_worksheet('Contract Expiry Report')
        sheet.write(0, 2, 'Contract Expiry Report', format1)
        sheet.write(3, 0, 'Expire Before: ' + str(data['date_expire']), format1)
        location = self.env['hr.location'].search([('id', '=', data['location_id'])])
        if not location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('date_end', '<', data['date_expire'])],
                                                             order='date_end asc')
        else:
            if location:
                active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                                  ('date_end', '<', data['date_expire']),
                                                                  ('employee_id.hr_location_id', 'in',
                                                                   data['location_id'])], order='date_end asc')
        location_extract = ''
        for loc in location:
            location_extract = location_extract + loc.name + ','

        sheet.write(3, 3, 'Location: ' + location_extract, format1)

        sheet.write(5, 0, 'EMP Code', format1)
        sheet.write(5, 1, 'Name', format1)
        sheet.write(5, 2, 'Location', format1)
        sheet.write(5, 3, 'Department', format1)
        sheet.write(5, 4, 'Employee Type', format1)
        sheet.write(5, 5, 'Date of Joining', format1)
        sheet.write(5, 6, 'Contract Expiry', format1)
        row = 6  # indicate After it New Line Generate
        if not active_contract:
            sheet.write(row + 2, 0, 'No Active Contract Found!!!!!!!!!!!!!!!!!!!!!', format1)
        width = 4
        sheet.set_column(0, 6, 24)
        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': False})
        for contract in active_contract:
            sheet.write(row, 0, str(contract.employee_id.emp_number), format2)
            sheet.write(row, 1, str(contract.employee_id.name), format2)
            sheet.write(row, 2, str(contract.employee_id.hr_location_id.name), format2)
            sheet.write(row, 3, str(contract.employee_id.department_id.name), format2)
            if contract.employee_id.emp_type == 'permanent':
                sheet.write(row, 4, str('Permanent'), format2)
            elif contract.employee_id.emp_type == 'contractor':
                sheet.write(row, 4, 'Contractor', format2)
            elif contract.employee_id.emp_type == 'freelancer':
                sheet.write(row, 4, 'FreeLancer', format2)
            elif contract.employee_id.emp_type == 'inter':
                sheet.write(row, 4, 'Intern', format2)
            elif contract.employee_id.emp_type == 'project_based':
                sheet.write(row, 4, 'Project Based Hiring', format2)
            else:
                sheet.write(row, 4, 'Outsource', format2)
            dated = str(contract.employee_id.date.day) + "-" + str(contract.employee_id.date.month) + "-" + str(
                contract.employee_id.date.year)
            sheet.write(row, 5, dated, format2)
            contract_dated = str(contract.date_end.day) + "-" + str(contract.date_end.month) + "-" + \
                             str(contract.date_end.year)
            sheet.write(row, 6, contract_dated, format2)
            row = row + 1
