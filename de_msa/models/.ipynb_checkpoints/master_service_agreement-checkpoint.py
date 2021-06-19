# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _



class master_service_agreement(models.Model):
    _name = 'master.service.agreement'

    
    name = fields.Char('Reference', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    head_lease_invoicing_limit = fields.Float('Lease Agreement Invoicing Limit')
    la_extra_special_division = fields.Boolean('LA Extra Computation')
    
    
    site_billing_info_ids = fields.One2many('site.billing.info', 'msa_id', string='Site Billing Information')
    tower_currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    tower_without_power_ids = fields.One2many('tower.without.power', 'msa_id', string='Tower w/o Power')
    power_currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    power_prices_ids = fields.One2many('power.prices', 'msa_id', string='Power Prices')
    location_factor_ids = fields.One2many('location.factor', 'msa_id', string='Location Factors')
    wind_factor_ids = fields.One2many('wind.factor', 'msa_id', string='Wind Factors')
    sla_factor_ids = fields.One2many('sla.factor', 'msa_id', string='SLA Factors')
    collocation_capex_ids = fields.One2many('collocation.discount.tower.capex', 'msa_id', string='Collocation Discount for Tower CAPEX')
    capex_comment = fields.Text('Comment for CAPEX')
    collocation_opex_ids = fields.One2many('collocation.discount.tower.opex', 'msa_id', string='Collocation Discount for Tower OPEX')
    opex_comment = fields.Text('Comment for OPEX')
    opex_cpi_ids = fields.One2many('opex.cpi', 'msa_id', string='Opex CPI')
    capex_escalation_ids = fields.One2many('capex.escalation', 'msa_id', string='CAPEX Escalation')
    penalty_ids = fields.One2many('msa.penalty', 'msa_id', string='Penalties')
    site_load_ids = fields.One2many('site.load', 'msa_id', string='Site Load')
    msa_simulation_ids = fields.One2many('msa.simulation', 'msa_id', string='Price Details', readonly=True)
    total_gross_capex = fields.Float(string='Total IP Fee CAPEX')
    total_gross_opex = fields.Float(string='Total IP Fee OPEX')
    number_days_in_month = fields.Float(string='Number Days In Month')
    diff_billing = fields.Boolean('Differential Billing')
    simulation_date = fields.Date('Simulation Date To')
    simulation_date_from = fields.Date('Simulation Date From')
    exchange_rate = fields.Float(string='Exchange Rate (from USD to MMK)', help="1 USD = ? MMK. '?' is the Exchange Rate.")
    invoice_date = fields.Date(string='Invoice Date')
    gross_ip_fee = fields.Float(string='Total Gross IP Fee')
    ip_fee = fields.Float(string='Total IP Fee')
    account_invoice_ids = fields.One2many('msa.invoice.line', 'msa_id')
    collocation_power_capex_ids = fields.One2many('collocation.discount.power.capex', 'msa_id', string='Collocation Discount for Power CAPEX')
    collocation_power_capex = fields.Text('Comment for Power CAPEX')
    target_pass_through_ids = fields.One2many('target.pass.through', 'msa_id', string='Target Pass-Through')

#         --------------- old fields ------------------
#     total_gross_ip_fee = fields.function(_cal_total, type='float', string='Total Gross IP Fee', multi='_cal_gross')
#     total_ip_fee = fields.function(_cal_total, type='float', string='Total IP Fee', multi='_cal_gross')
#     exchange_rate = fields.Float('Exchange Rate (from USD to MMK)', help="1 USD = ? MMK. '?' is the Exchange Rate.")
#     total_gross_capex = fields.function(_cal_total, type='float', string='Total IP Fee CAPEX', multi='_cal_gross')
#     total_gross_opex = fields.function(_cal_total, type='float', string='Total IP Fee OPEX', multi='_cal_gross')
#     number_days_in_month = fields.function(get_number_days_in_month, type='float', string='Number Days In Month'
#                                 store={'master.service.agreement': (lambda self, cr, uid, ids, context=None: ids, ['simulation_date'], 10)})
#         ---------------- Ends Here -------------------