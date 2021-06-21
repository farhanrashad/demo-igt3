# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
#from datetime import datetime
#import datetime as dt
import datetime

from dateutil.relativedelta import relativedelta
import traceback

from ast import literal_eval
from collections import Counter
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import format_date, float_compare
from odoo.tools.float_utils import float_is_zero

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    allow_warranty = fields.Boolean(string='Allow Warranty', compute="_compute_allow_warranty")
    
    warranty_date_start = fields.Char(string='WTY Start')
    warranty_date_end = fields.Char(string='WTY End')
    warranty_days = fields.Char(string='WTY Days')
    
    w_date = fields.Date(compute="_compute_date")
    #warranty_date_start = fields.Date(string='WTY Start')
    #warranty_date_end = fields.Date(string='WTY End')
    #warranty_days = fields.Integer(string='WTY Days', compute='_compute_warranty_days')
    
    @api.depends('product_id','warranty_date_start','warranty_date_end')
    def _compute_date(self):
        date_string = ''
        for line in self:
            #d = dt.datetime.strptime(line.warranty_date_start, "%d-%m-%Y")
            #d = d.date()
            #line.w_date = d.isoformat()

            #date_string = line.warranty_date_start
            #line.w_date = (datetime.fromisoformat(date_string))
            line.w_date = datetime.datetime.strptime(line.warranty_date_start, "%d-%m-%Y").date()
            
    @api.depends('product_id')
    def _compute_allow_warranty(self):
        for stock in self:
            stock.allow_warranty = stock.product_id.product_tmpl_id.allow_warranty
            
    #@api.depends('warranty_date_start','warranty_date_end')
    def _compute_warranty_days(self):
        days = 0
        for stock in self:
            if stock.warranty_date_start and stock.warranty_date_end:
                rdelta = relativedelta(stock.warranty_date_end, stock.warranty_date_start)
                days = rdelta.days
            stock.warranty_days = days
    
