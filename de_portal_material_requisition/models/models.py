# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockTransferOrder(models.Model):
    _inherit = 'stock.transfer.order'

class StockTransferOrderType(models.Model):
    _inherit = 'stock.transfer.order.type'

class StockTransferOrderLine(models.Model):
    _inherit = 'stock.transfer.order.line'

class StockTransferOrderCategory(models.Model):
    _inherit = 'stock.transfer.order.category'


class StockTransferReturnLine(models.Model):
    _inherit = 'stock.transfer.return.line'

class StockPicking(models.Model):
    _inherit = 'stock.picking'

class StockMove(models.Model):
    _inherit = 'stock.move'

class StockMoveline(models.Model):
    _inherit = 'stock.move.line'

class ResPartner(models.Model):
    _inherit = 'res.partner'


class StockTransferOrder(models.Model):
    _inherit = 'stock.transfer.order.stage'


