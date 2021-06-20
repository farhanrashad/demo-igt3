from datetime import datetime
import math
import openerp.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class msa_simulation(models.Model):
    _name = 'msa.simulation'
    
    def compute_values(self):
        for rec in self:
            if rec.month_days > 0:
    #             ((Tower Capex Rate*Regional Factor*Wind Factor*Collocation Discount)/No. of Days in Month)*Invoicing Days*Capex CPI
                ip_fee_capex = ((rec.gross_ip_fee_capex * rec.region_factor * rec.wind_factor * rec.collocation_capex)/rec.month_days) * rec.invoicing_days * rec.capex_escalation
                
    #             ((Tower Opex Rate*Regional Factor*SLA Factor*Collocation Discount*Exchange Rate)/No. of Days in Month)* Invoicing Days
                rec.ip_fee_opex = ((rec.gross_ip_fee_opex * rec.region_factor * rec.collocation_opex * rec.msa_id.exchange_rate) / rec.month_days) * rec.invoicing_days
                
    #             ((Power Capex Rate*Regional Factor*Collocation Discount)/No. of Days in Month)*Invoicing Days*Capex CPI
                rec.power_fee_capex = ((rec.power_price_capex * rec.region_factor * rec.collocation_capex) / rec.month_days) * rec.invoicing_days * rec.capex_escalation
        
    #             (200-(Monthly Lease Amount/Exchange Rate))/(No.of Tenants+1)
                rec.head_lease = (200-(rec.monthly_lease_amount / rec.msa_id.exchange_rate)) / (rec.no_of_tenants_capex+1)
                
    #             Tower w/o Power Capex + Power Capex
                rec.ip_fee_capex = ip_fee_capex + rec.power_fee_capex
                
            else:
                rec.ip_fee_opex = 0
                rec.power_fee_capex = 0 
                rec.head_lease = 0
                rec.ip_fee_capex = 0 
    
    
    
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
    site_billing_info_id = fields.Many2one('site.billing.info', 'Site Billing Info')
    site_id = fields.Many2one('project.project', string='Site', readonly=True)
    region_factor = fields.Float('Region Factor')
    year = fields.Float(string='Year')
    head_lease_full_extra = fields.Boolean('Head Lease Full Extra', readonly=True)
    inv_tower_type = fields.Many2one('product.product', 'Tower Type', readonly=True)
    inv_power_model = fields.Many2one('product.product', 'Power Model', readonly=True)
    ip_fee_capex = fields.Float(string='Tower w/o Power CAPEX', compute='compute_values')
    ip_fee_opex = fields.Float('Tower w/o Power OPEX', compute='compute_values')
    power_fee_capex = fields.Float('Power CAPEX', compute='compute_values')
    opex_cpi = fields.Float(string='CPI OPEX')
    capex_escalation = fields.Float('CPI CAPEX')
    collocation_capex = fields.Float(string='Collocation Discount for Tower CAPEX')
    collocation_opex = fields.Float(string='Collocation Discount for Tower OPEX')
    head_lease = fields.Float('Lease Agreement', compute='compute_values')
    head_lease_extra = fields.Float('Lease Agreement Extra')
    num_of_tenant = fields.Float(string='Number of Tenants')
    gross_ip_fee_capex = fields.Float('IP Fee CAPEX')
    gross_ip_fee_opex = fields.Float('IP Fee OPEX')
    gross_ip_fee = fields.Float('Gross IP Fee')
    ip_fee = fields.Float('IP Fee')
    wind_factor =  fields.Float(string='Wind Factor')
    sla_factor = fields.Float(string='SLA Factor')
    invl_fuel_total = fields.Float('Last Month Energy Bill Fuel')
    invl_enegry_total = fields.Float('Last Month Energy Bill Electricity')
    invoicing_days = fields.Integer('Invoicing Days')
    invoiced_rent_adjustment = fields.Float('Invoiced Rent Adjustment')
    mini_cluster = fields.Char('Mini Cluster')
    cluster = fields.Many2one('site.cluster', 'Cluster')
    month_year = fields.Char('Month Year')
    ip_start_date = fields.Date('IP Fee Start Date', readonly=True)
    simulation_date = fields.Date('Simulation Date')
    ip_fee_capex_billed = fields.Float('IP Fee Capex Billed')
    diff_capex = fields.Float('Diff. Capex')
    ip_fee_opex_billed = fields.Float('IP fee Opex billed')
    diff_opex = fields.Float('Diff. Opex')
    month_days = fields.Integer()
    power_price_capex = fields.Float()
    monthly_lease_amount = fields.Float()
    no_of_tenants_capex = fields.Integer()
    
    
    
    