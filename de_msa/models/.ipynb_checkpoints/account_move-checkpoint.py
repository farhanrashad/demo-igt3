# coding: utf-8

from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
    
    
class AccountMoveInh(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move MSA'
    
    msa_id = fields.Many2one('master.service.agreement', string='MSA')
    category = fields.Selection([('Capex','Capex'),('Opex','Opex')], default='Capex')
    
    
    
        
    
