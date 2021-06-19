# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError

class CustomEntryType(models.Model):
    _inherit = 'account.custom.entry.type'
    
    category_id = fields.Many2one('approval.category', string="Category", required=False)

   
