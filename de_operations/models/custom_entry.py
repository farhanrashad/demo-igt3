# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta

import json
from lxml import etree

class CustomEntryType(models.Model):
    _inherit = 'account.custom.entry.type'
    
    allow_advance_inv = fields.Boolean(string='Allow Advance')
    dp_product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],)
    
class CustomEntry(models.Model):
    _inherit = 'account.custom.entry'
    
    allow_advance_inv = fields.Boolean(related='custom_entry_type_id.allow_advance_inv')

    
    