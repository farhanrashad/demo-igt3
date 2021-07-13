# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ContractExpiryPDF(models.AbstractModel):
    _name = 'report.de_hr_employee_report.contract_pdf_report'
    _description = 'Contract PDF Report'

    def _get_report_values(self, docids, data):
        # location = self.env['hr.work.location'].search([('id', '=', data['location_ids'])])
        location = self.env['hr.location'].search([('id', '=', data['location_ids'])])
        location_extract = ''
        for loc in location:
            location_extract = location_extract + loc.name + ','
        if location:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('date_end', '<', data['date_expire']),
                                                              ('employee_id.hr_location_id', 'in',
                                                               data['location_ids'])], order='date_end asc')
        else:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('date_end', '<', data['date_expire'])], order='date_end asc')

        return {
            'doc_ids': self.ids,
            'doc_model': 'contract.expiry.wizard',
            'data': data,
            'location': location_extract,
            'active_contract': active_contract,
        }
