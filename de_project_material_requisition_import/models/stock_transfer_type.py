# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
_logger = logging.getLogger(__name__)
import io



class StockTransferType(models.Model):
    _inherit = 'stock.transfer.order.type'

    is_publish = fields.Boolean(string='Publish on Website')


