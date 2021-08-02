# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta

import json
from lxml import etree

class CustomEntry(models.Model):
    _inherit = 'account.custom.entry'
    
    #App fields
    has_om = fields.Selection(related="custom_entry_type_id.has_om")
    
class CustomEntryLine(models.Model):
    _inherit = 'account.custom.entry.line'
    
    #OM line Item Fields
    o_tower_type = fields.Selection([
        ('COW', 'COW'),
        ('GBT', 'GBT'),
        ('RTP', 'RTP')],
        string='OM Tower Type')
    o_product_id = fields.Many2one('product.product', string="OM Power Model Product", check_company=True)
    o_date_rfi = fields.Date(string='RFI Date', )
    o_date_onair = fields.Date(string='On Air Date', )
    o_date_handover = fields.Date(string='Handover Date', )
    o_date_start = fields.Date(string='Start Date', )
    o_date_end = fields.Date(string='End Date', )
    o_days_rfi = fields.Integer(string='RFI Days')
    o_days_onair = fields.Integer(string='On Air Days')
    o_amount = fields.Float(string='OM Amount' )
    o_final_amount = fields.Float(string='OM Final Amount' )
    o_charges = fields.Float(string='OM Service Charges' )

    
    