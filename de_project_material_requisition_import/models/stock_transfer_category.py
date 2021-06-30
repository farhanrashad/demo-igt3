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



class StockTransferCategory(models.Model):
    _inherit = 'stock.transfer.order.category'

    is_publish = fields.Boolean(string='Publish on Website')
    health_check_form = fields.Boolean(string='Health Check Form')
    fir_report = fields.Boolean(string='FIR Report')
    accident_report = fields.Boolean(string='Accident Report')
    hoto_checklist = fields.Boolean(string='HOTO Checklist')
    attachment_count = fields.Integer(string='Attachment Count', default=1)




