from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractExpiryWizard(models.TransientModel):
    _name = 'contract.expiry.wizard'
    _description = 'Contract Expiry Wizard'

    date_expire = fields.Date('Expire Before')
    # location_id = fields.Many2many('hr.work.location', string='Location')
    location_id = fields.Many2many('hr.location', string='Location')

    def action_gnerate_pdf(self):
        data = {'date_expire': self.date_expire, 'location_ids': self.location_id.ids}
        return self.env.ref('de_hr_employee_report.action_report_contract_expiry').report_action(self, data=data)

    def action_gnerate_excel(self):
        datas = {
            'date_expire': self.date_expire,
            'location_id': self.location_id.ids,
        }
        return self.env.ref('de_hr_employee_report.view_contract_report_xlsx').report_action(self, data=datas)
