# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
from dateutil import parser
import ast
from datetime import timedelta, datetime
from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR


import logging
_logger = logging.getLogger(__name__)
import io
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ProjectProject(models.Model):
    _inherit = 'project.project'


class ProjectTask(models.Model):
    _inherit = 'project.task'


    entry_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_entry",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Entry Attachment")


    custom_entry_type_id = fields.Many2one('account.custom.entry.type', string='Entry Type')
    entry_partner_id = fields.Many2one('res.partner', string='Contractor')
    custom_entry_id = fields.Many2one('account.custom.entry', string='Entry')
    is_entry_attachment = fields.Boolean(string='Is Entry Attachment')
    is_entry_processed = fields.Boolean(string='Entry Processed')
    un_processed_entry = fields.Boolean(string='Un-Processed Entry')
    
    
    @api.model_create_multi
    def create(self, vals_list):
        default_stage = dict()
        for vals in vals_list:
            project_id = vals.get('project_id') or self.env.context.get('default_project_id')
            if project_id and not "company_id" in vals:
                vals["company_id"] = self.env["project.project"].browse(
                    project_id
                ).company_id.id or self.env.company.id
            if project_id and "stage_id" not in vals:
                # 1) Allows keeping the batch creation of tasks
                # 2) Ensure the defaults are correct (and computed once by project),
                # by using default get (instead of _get_default_stage_id or _stage_find),
                if project_id not in default_stage:
                    default_stage[project_id] = self.with_context(
                        default_project_id=project_id
                    ).default_get(['stage_id']).get('stage_id')
                vals["stage_id"] = default_stage[project_id]
            # user_id change: update date_assign
            if vals.get('user_id'):
                vals['date_assign'] = fields.Datetime.now()
            # Stage change: Update date_end if folded stage and date_last_stage_update
            if vals.get('stage_id'):
                vals.update(self.update_date_end(vals['stage_id']))
                vals['date_last_stage_update'] = fields.Datetime.now()
            # recurrence
            rec_fields = vals.keys() & self._get_recurrence_fields()
            if rec_fields and vals.get('recurring_task') is True:
                rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
                rec_values['next_recurrence_date'] = fields.Datetime.today()
                recurrence = self.env['project.task.recurrence'].create(rec_values)
                vals['recurrence_id'] = recurrence.id
        tasks = super().create(vals_list)
        for task in tasks:
            if task.project_id.privacy_visibility == 'portal':
                task._portal_ensure_token()
#         if  tasks.entry_attachment_id.id:       
#             tasks.action_journal_entry_import()
                
        return tasks
    

    @api.constrains('entry_attachment_id')
    def _check_attachment(self):
        if self.entry_attachment_id:
            self.is_entry_attachment = True
            self.un_processed_entry = True

	
    def action_journal_entry_import(self):
        keys = []
        ir_model_fields_obj = self.env['ir.model.fields']
        custom_entry_obj = self.env['account.custom.entry']
        custom_entry_obj_line = self.env['account.custom.entry.line']

        for custom in self:
            if custom.is_entry_processed == False:
                counter = 1
                try:
                    file = str(base64.decodebytes(custom.entry_attachment_id.datas).decode('utf-8'))
                    file_reader = csv.reader(file.splitlines())
                    skip_header = True

                except:
                    raise  UserError('Invalid File Format!')
                count = 0
                for row in file_reader:
                    for row_val in  row:

                        search_field = ir_model_fields_obj.sudo().search([
                            ("model", "=", "account.custom.entry.line"),
                            ("field_description", "=", row_val),
                        ], limit=1)
                        keys.append(search_field.name)

                    break
                rowvals = []
                vals = []
                line_vals = {}
                custom_entry_id_vals = self.custom_entry_id.id
                if self.custom_entry_id:
                    custom_entry_id_vals = self.custom_entry_id.id
                    entry = self.env['account.custom.entry'].search([('id','=', self.custom_entry_id.id)])
                    for entry_line in entry.custom_entry_line:
                        entry_line.unlink()    
                            
                else:    
                    partner = custom.entry_partner_id.id
                    user = custom.user_id.id
                    custom_vals = {
                        'date_entry': fields.datetime.now(),
                        'partner_id': partner,
                        'user_id': user,
                        'custom_entry_type_id': self.custom_entry_type_id.id,
                    }
                    custom_entry = self.env['account.custom.entry'].create(custom_vals)
                    custom_entry_id_vals = custom_entry.id
                for data_row in file_reader:
                    inner_vals = {}
                    index = 0
                    i = 0
                    for data_column in data_row:
#                         raise UserError(str(custom_entry.id))
                        inner_vals.update({
                            'custom_entry_id': custom_entry_id_vals
                        })
                        rowvals.append(data_row)
                        search_field = ir_model_fields_obj.sudo().search([
                            ("model", "=", "account.custom.entry.line"),
                            ("name", "=", keys[i]),
                        ], limit=1)
                        if search_field.ttype == 'many2one' and search_field.name == 'car_details':

                            many2one_vals = self.env[str(search_field.relation)].search([('display_name','=',data_column)], limit=1)

                            inner_vals.update({
                                keys[i]: many2one_vals.id
                            })
                            index = index + 1
                            i = i + 1
                        elif search_field.ttype == 'many2one':

                            many2one_vals = self.env[str(search_field.relation)].search([('name','=',data_column)], limit=1)

                            inner_vals.update({
                                keys[i]: many2one_vals.id
                            })
                            index = index + 1
                            i = i + 1
                        elif search_field.ttype == 'date':
                            date_parse = parser.parse(data_column)
                            date_vals = date_parse.strftime("%Y-%m-%d")
                            inner_vals.update({
                                keys[i]: date_vals
                            })
                            index = index + 1
                            i = i + 1
                        elif search_field.ttype == 'datetime':
                            datetime_parse = parser.parse(data_column)
                            datetime_vals = datetime_parse.strftime("%Y-%m-%d %H:%M:%S")
                            inner_vals.update({
                                keys[i]: datetime_vals
                            })
                            index = index + 1
                            i = i + 1

                        else:
                            if keys[i] != False:
                                inner_vals.update({
                                        keys[i] : data_column
                                    })
                            index = index + 1
                            i = i + 1
                    vals.append(inner_vals)
                try:
                    custom_entry_obj_line.create(vals)
                except Exception as e:
                    raise UserError(e)
                custom.is_entry_processed = True
                custom.un_processed_entry = False
                custom.user_id = self.env.user.id


class CustomEntryType(models.Model):
    _inherit = 'account.custom.entry.type'
    
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'   
    
    
class ResGroups(models.Model):
    _inherit = 'res.groups'     

