from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GtnDgnMrfSpmrfWizard(models.TransientModel):
    _name = "spare.penalty.wizard"
    _description = "Spare Penalty Wizard"
    
    src =  fields.Datetime(string='From',required=True)
    dest =  fields.Datetime(string='To',required=True)
    
    def generate_report(self):
        #order_ids = self.env['stock.transfer.order'].browse(self._context.get('active_ids',[]))
        data = {'start_date': self.src, 'end_date': self.dest}
        if self.src < self.dest:
            return self.env.ref('de_spare_penalty_report.spare_penalty_report').report_action(self, data=data)
