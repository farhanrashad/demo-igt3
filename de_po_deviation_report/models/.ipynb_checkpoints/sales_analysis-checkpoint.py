from odoo import models, api

class SalesAnalysis(models.TransientModel):
    _inherit = 'pos.details.wizard'

    def sale_analysis_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date, 'config_ids': self.pos_config_ids.ids}
        if self.start_date < self.end_date:
            return self.env.ref('de_pos_sales_report.sale_analysis_report').report_action(self, data=data)