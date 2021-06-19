# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockTransferCloseReason(models.Model):
    _name = "stock.transfer.close.reason"
    _order = "sequence, id"
    _description = "Stock Transfer Close Reason"

    name = fields.Char('Reason', required=True, translate=True)
    sequence = fields.Integer(default=10)
    reason_type = fields.Selection([
        ('normal','Normal'),
        ('delivery','Auto Delivery Expiry'),
        ('return','Auto Return Expiry'),
    ],default='normal', )