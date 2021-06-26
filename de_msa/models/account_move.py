# coding: utf-8

import datetime
from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
    
    
class AccountMoveInh(models.Model):
    _inherit = 'account.move'
    
    msa_id = fields.Many2one('master.service.agreement')
    category = fields.Selection([('Capex','Capex'),('Opex','Opex')])
    
    
    
        
    
