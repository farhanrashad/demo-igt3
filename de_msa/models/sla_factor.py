# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class sla_factor(models.Model):
    _name = 'sla.factor'
    _description = 'SLA Factor'

    name = fields.Many2one('sla.factor.value', required=True)
    factor = fields.Float('Factor')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')

    
    

class sla_factor_value(models.Model):
    _name = 'sla.factor.value'
    _description = 'SLA Factor Value'

    name = fields.Char('Name', required=True)
