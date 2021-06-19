from odoo import models, fields, api

class MSAInvoice(models.Model):
    _name = 'msa.invoice.line'
    _description = 'MSA Invoice'


    msa_id = fields.Many2one('master.service.agreement', string='msa')
    supplier_invoice_number = fields.Integer(string='Supplier Invoice Number')
    partner_id= fields.Many2one('res.partner', string='Partner')
    date_invoice = fields.Date(string='Invoice Date')
    number = fields.Integer(string='Number')
    category = fields.Char(string='Category')
    company_id = fields.Char(string='Regional Name')
    user_id = fields.Char(string='Responsible')
    date_due = fields.Char(string='Due Date')
    origin = fields.Char(string='Source Document')
    currency_id = fields.Many2one('res.currency', string='Invoice Currency')
    residual = fields.Char(string='Regional Name')
    amount_untaxed = fields.Char(string='Balance')
    sub_total = fields.Float(string='Balance')
    amount_total = fields.Float(string='Amount Total')
    amount_total_usd = fields.Float(string='Amount Total USD')
