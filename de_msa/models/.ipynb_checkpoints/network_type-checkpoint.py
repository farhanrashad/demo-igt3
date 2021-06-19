# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class network_type(models.Model):

    _name = 'network.type'

    
    name = fields.Char('Name')
