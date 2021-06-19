# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class sla_factor(models.Model):
    _name = 'sla.factor'

    name = fields.Many2one('sla.type', 'SLA Type', required=True)
    factor = fields.Float('Factor')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')
