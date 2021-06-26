# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class wind_factor(models.Model):
    _name = 'wind.factor'

    name = fields.Many2one('wind.category', 'Name', required=True)
    factor = fields.Float('Factor')
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement')