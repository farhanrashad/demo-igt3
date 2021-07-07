from odoo import models, fields, api

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                       , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                       , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                       , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                       , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                                   string="Target Year", related = 'holiday_status_id.target_year')

#for Hr.leave.report additional Fields target date
class HrLeaveReport(models.Model):
    _inherit = 'hr.leave.report'

    target_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                       , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                       , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                       , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                       , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                                   string="Target Year", related = 'holiday_status_id.target_year')
