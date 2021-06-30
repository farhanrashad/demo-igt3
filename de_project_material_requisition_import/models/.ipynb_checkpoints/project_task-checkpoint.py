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


class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_project_task",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment")

	
    def action_material_import(self):
        
        keys = ['transfer_order_type_id',  'user_id', 'transfer_order_category_id', 'company_id', 'purchase_id', 'transporter_id']
        try:
            csv_data = base64.b64decode(self.attachment_id.datas)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            values = {}
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
        except:
            raise UserError(_("Invalid file!"))

    
        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            values = dict(zip(keys, field))
            if values:
                if i == 0:
                    continue
                else:
                    values.update({
                            'transfer_order_type_id' : field[0],
                            'user_id' : field[1],
                            'transfer_order_category_id' : field[2],
                            'company_id'  : field[3],
                            'purchase_id'  : field[4],
                            'transporter_id': field[5],

                    })
                    res = self.create_transfer_order(values)
                    
                    
    
    def create_transfer_order(self,values):

        if values.get("transfer_order_type_id") == "":
            raise UserError(_('Transfer Type field cannot be empty.') )

        if values.get("user_id") == "":
            raise UserError(_('Request Owner field cannot be empty.') )

        if values.get("transfer_order_category_id") == "":
            raise UserError(_('Category field cannot be empty.'))
            
        if values.get("company_id") == "":
            raise UserError(_('Company field cannot be empty.'))

        if values.get("purchase_id") == "":
            raise UserError(_('Purchase Order field cannot be empty.'))


        if values.get("transporter_id") == "":
            raise UserError(_('Transporter field cannot be empty.'))


        transfer_type = self.find_transfer_type(values.get('transfer_order_type_id'))
        user_id = self.find_requested_owner(values.get('user_id'))
        category = self.find_transfer_category(values.get('transfer_order_category_id'))
        company = self.find_company(values.get('company_id'))
        purchase_order = self.find_purchase_order(values.get('purchase_id'))
        transporter = self.find_transporter(values.get('transporter_id'))

        transfer_order = self.env['stock.transfer.order']

        data =  {
                'transfer_order_type_id' : transfer_type.id,
                'sequence_code': transfer_type.code,
                'user_id' : user_id.id,
                'transfer_order_category_id':category.id,
                'company_id':company.id,
                'purchase_id':purchase_order.id,
                'transporter_id':transporter.id,

                }
        torder = transfer_order.create(data)
        
        return torder
        
    def find_transfer_type(self,type):
        transfer_type =self.env['stock.transfer.order.type']
        transfer_search = transfer_type.search([('name','=',type)])
        if transfer_search:
            return transfer_search
        else:
            raise UserError(_('Field Transfer Type is not correctly set.'))
    
        
    def find_requested_owner(self,user):
        request_user =self.env['res.users']
        user_search = request_user.search([('partner_id.name','=',user)])
        if user_search:
            return user_search
        else:
            raise UserError(_('Field Requested Owner is not correctly set.'))
    
        
    def find_transfer_category(self,category):
        request_category =self.env['stock.transfer.order.category']
        category_search = request_category.search([('name','=',category)])
        if category_search:
            return category_search
        else:
            raise UserError(_('Field Transfer Category is not correctly set.'))
    
        
    def find_company(self,company):
        rquest_company =self.env['res.company']
        company_search = rquest_company.search([('name','=',company)])
        if company_search:
            return company_search
        else:
            raise UserError(_('Field Comapany is not correctly set.'))
    

    def find_purchase_order(self,purchase):
        purchase_order =self.env['purchase.order']
        order_search = purchase_order.search([('name','=',purchase)])
        if order_search:
            return order_search
        else:
            raise UserError(_('Field Purchase Order is not correctly set.'))

    
    def find_transporter(self,transporter):
        request_transporter =self.env['res.partner']
        transporter_search = request_transporter.search([('name','=',transporter)], limit=1)
        if transporter_search:
            return transporter_search
        else:
            raise UserError(_('Field Transporter is not correctly set.'))


