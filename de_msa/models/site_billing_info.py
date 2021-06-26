# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class site_billing_info(models.Model):
    _name = 'site.billing.info'

    
#     @api.model
#     def create(self, vals):
#         record_exists = self.search([('site_id', '=', vals['site_id'])])
# 
#         if record_exists:
#             raise UserError(('Site ('+str(record_exists.site_id.name)+') in the current MSA already exists!'))
#         else:
#             pass
#            
#         rec = super(site_billing_info, self).create(vals)
#         return rec
    
    def compute_name(self):
        for rec in self:
            if rec.site_id:
                rec.name = rec.site_id.name
            else:
                rec.name = None
    

    name = fields.Char('Customer Site Reference', compute='compute_name')
    site_id = fields.Many2one('project.project', string='Site')
    site_tower_type = fields.Many2one('product.product', 'Site Tower Type')
    inv_tower_type = fields.Many2one('product.product', 'Invoiced Tower Type')
    site_power_model = fields.Many2one('product.product', 'Site Power Model')
    inv_power_model = fields.Many2one('product.product', 'Invoiced Power Model')
    indoor_bts = fields.Integer('# Indoor BTS', help="This is used for the O&M to be able to control the energy consumption.")
    outdoor_bts = fields.Integer('# Outdoor BTS', help="This is used for the O&M to be able to control the energy consumption.")
    ip_start_date = fields.Date('IP Fee Start Date')
    ip_end_date = fields.Date('IP Fee End Date')
    billable = fields.Boolean('Billable', help="Flag indicating that the site is now eligible for billing (this should be linked to the 80% cluster rule for Telenor")
    head_lease_full_extra = fields.Boolean('Lease Agreement Full Extra')
    billable_lease_amount = fields.Float('Billable Lease Amount', required=True)
    network_type_id = fields.Many2one('network.type', 'Network Type')
    site_class = fields.Selection([('critical', 'Critical'), ('normal', 'Normal')], 'Site Class')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')  
    
    