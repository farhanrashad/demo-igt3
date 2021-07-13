import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import base64



class PayslipBatch(models.TransientModel):
    _name = "pay.slip.batch"
    _description = "Payslip Batch Wizard"

    contract_type = fields.Selection([('local', 'Local'),('expats', 'Expats')], string='Contract Type')
    doe = fields.Date(string='Date of Execution')
    debit_ac_no = fields.Float(string='Debit A/C No.')
    currency = fields.Many2one('res.currency', string='Currency')
    batch_id = fields.Many2one('hr.payslip.run')
    date_today = fields.Date(default=datetime.today())
    
    def print_report(self):
        print('ID: ', self.id)
        datas = {
            'contract_type': self.contract_type,
            'doe': self.doe,
            'debit_ac_no': self.debit_ac_no,
            'currency': self.currency.id,
            'id': self.batch_id.id,
        }
        return self.env.ref('de_payslip_batch_report.payslip_batch_report').report_action(self, data=datas)
    
    
    
    def print_txt_report(self):
        data_val = ''
        vals = ''
        filename = "batch.txt"
        file_ = open(filename + str(), 'w')
        payslips = self.env['hr.payslip'].search([('payslip_run_id', '=', self.batch_id.id)])
        line = ' ' 
        for payslip in payslips:
            line += 'TT' + '  ' + str(payslip.number) + '        ' + str(self.debit_ac_no) + '  ' + str(self.currency.name) + str(self.date_today) + '   ' + str(payslip.net_wage) + '         ' + str(payslip.employee_id.bank_account_id.acc_number) + '                    ' + str(payslip.employee_id.address_id.street)+ '  '+ str(payslip.employee_id.address_id.street2) + ' '+ str(payslip.employee_id.address_id.city) + ' ' + str(payslip.employee_id.address_id.country_id.name) + '                              ' + str(payslip.employee_id.bank_account_id.bank_id.name)  + '     ' + str(payslip.employee_id.bank_account_id.bank_id.street) + ' ' + str(payslip.name) + str(payslip.employee_id.work_email) +"\n"
        data_val = str(line)
        file_.write(data_val)
        file_.write("\n")
        file_.close()
        
        with open('batch.txt') as f:
            read_file = f.read()
            attachment_vals = {
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(read_file.encode('utf8')),
                    'res_id': self.batch_id.id,
                    'res_name': self.batch_id.name,
                    'res_model': 'hr.payslip.run',
            }
            attach_file = self.env['ir.attachment'].create(attachment_vals)
            download_url = '/web/content/' + str(attach_file.id) + '?download=True'
            #base_url = self.env['ir.config_parameter'].get_param('web.base.url')
#             Return so it will download in your system
            return {
                    "type": "ir.actions.act_url",
                    "url": str(download_url),
                    "target": "new",
            }
        
        

