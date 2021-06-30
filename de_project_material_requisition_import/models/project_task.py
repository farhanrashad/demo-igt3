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
from dateutil import parser
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


    transfer_category_id = fields.Many2one('stock.transfer.order.category', string='Transfer Category')
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Requisition Attachment")

    fir_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_fir",
                                     column1="doc_id",
                                     column2="fir_attachment_id",
                                     string="FIR Report")

    expiry_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_expiry",
                                         column1="doc_id",
                                         column2="expiry_attachment_id",
                                         string="Expiry Attachment")
    check_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_check",
                                         column1="doc_id",
                                         column2="check_attachment_id",
                                         string="Health Check Form")

    accident_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_accident",
                                           column1="doc_id",
                                           column2="accident_attachment_id",
                                           string="Accident Report")

    checklist_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task_checklist",
                                              column1="doc_id",
                                              column2="checklist_attachment_id",
                                              string="Hoto Checklist")



    transfer_categ = fields.Char(string='Category')
    is_attachment = fields.Boolean(string='Is Attachment')
    is_requisition = fields.Boolean(string='Is Requisition')
    is_fir = fields.Boolean(string='Is FIR')
    is_check_form = fields.Boolean(string='Is Check Form')
    is_checklist = fields.Boolean(string='Is Checklist')
    is_accidnent = fields.Boolean(string='Is Accident')
    is_expiry = fields.Boolean(string='Is Expiry')

    is_processed = fields.Boolean(string='Processed')
    un_processed = fields.Boolean(string='Un-Processed')

    @api.constrains('attachment_id')
    def _check_requisition_attachment(self):
        if self.attachment_id:
            self.is_attachment = True
            self.un_processed = True


    def action_submit(self):
        no_attachment = self.transfer_category_id.no_of_attachment
        count_attachment = 0
        attachments = self.env['ir.attachment'].search([('res_id','=',self.id)])
        for attach in attachments:
            count_attachment  = count_attachment + 1


	
    def action_material_import(self):
        keys = []
        ir_model_fields_obj = self.env['ir.model.fields']
        transfer_entry_obj = self.env['stock.transfer.order']
        transfer_entry_obj_line = self.env['stock.transfer.order.line']

        for transfer in self:
            if transfer.is_processed == False:
                vals = []
                counter = 0
                try:
                    file = str(base64.decodebytes(transfer.attachment_id.datas).decode('utf-8'))
                    file_reader = csv.reader(file.splitlines())
                    skip_header = True

                except:
                    raise UserError('Invalid File Format!')
                count = 0
                for row in file_reader:
                    for row_val in row:
                        search_field = ir_model_fields_obj.sudo().search([
                            ("model", "=", "stock.transfer.order.line"),
                            ("name", "=", row_val),
                        ], limit=1)
                        keys.append(search_field.name)

                    break
                rowvals = []
                line_vals = {}
                partner = transfer.user_id.partner_id.id
                transfer.entry_partner_id = transfer.user_id.partner_id.id
                stock_transfer = self.env['stock.transfer.order.type'].search([('name','=', transfer.name)], limit=1)
                custom_vals = {
                    'transfer_order_type_id': stock_transfer.id,
                    'sequence_code': stock_transfer.code,
                    'partner_id': partner,
                    'transfer_order_category_id': self.transfer_category_id.id,
                    'date_request': fields.datetime.now(),
                    'date_order': fields.datetime.now(),
                }
                transfer_entry = self.env['stock.transfer.order'].create(custom_vals)
               
                for data_row in file_reader:
                    inner_vals = {}
                    counter = counter + 1
                    index = 0
                    i = 0
                    for data_column in data_row:
                        inner_vals.update({
                            'stock_transfer_order_id': transfer_entry.id
                        })
                        rowvals.append(data_row)
                        search_field = ir_model_fields_obj.sudo().search([
                            ("model", "=", "stock.transfer.order.line"),
                            ("name", "=", keys[i]),
                        ], limit=1)

                        if search_field.ttype == 'many2one':

                            many2one_vals = self.env[str(search_field.relation)].search([('name', '=', data_column)],
                                                                                        limit=1)

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
                                    keys[i]: data_column
                                })
                            index = index + 1
                            i = i + 1
                    vals.append(inner_vals)

                transfer_entry_obj_line.create(vals)
                transfer.is_processed = True
                transfer.un_processed = False
                transfer.user_id = self.env.user.id
