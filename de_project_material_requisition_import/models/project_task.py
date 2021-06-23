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


    is_attachment = fields.Boolean(string='Is Attachment')
    is_requisition = fields.Boolean(string='Is Requisition')
    is_fir = fields.Boolean(string='Is FIR')
    is_check_form = fields.Boolean(string='Is Check Form')
    is_checklist = fields.Boolean(string='Is Checklist')
    is_accidnent = fields.Boolean(string='Is Accident')
    is_expiry = fields.Boolean(string='Is Expiry')

    is_processed = fields.Boolean(string='Processed')
    un_processed = fields.Boolean(string='Un-Processed')

    @api.constrains('attachment_id', 'fir_attachment_id')
    def _check_attachment(self):
        if self.fir_attachment_id:
            self.is_attachment = True
            self.un_processed = True
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
        for material in self:
            keys = ['transfer_order_type_id', 'user_id', 'transfer_order_category_id', 'company_id', 'purchase_id',
                    'transporter_id', 'partner_id', 'date_request', 'date_order', 'date_scheduled', 'delivery_deadline',
                    'date_delivered', 'date_returned', 'transfer_exception_type_id', 'reference', 'stock_transfer_order_id',
                    'picking_type_id', 'location_src_id', 'location_dest_id', 'return_location_id']
            try:
                csv_data = base64.b64decode(material.attachment_id.datas)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except:
                try:
                    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                    fp.write(binascii.a2b_base64(material.attachment_id.datas))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)

                except:
                    raise UserError(_("Invalid file Format!"))

                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:

                        line = list(map(
                            lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                        values.update({
                            'partner_id': line[0],
                            'transfer_order_type_id': line[1],
                            'user_id': line[2],
                            'transfer_order_category_id': line[3],
                            'company_id': line[4],
                            'purchase_id': line[5],
                            'transporter_id': line[6],
                            'date_request': line[7],
                            'date_order': line[8],
                            'date_scheduled': line[9],
                            'delivery_deadline': line[10],
                            'date_delivered': line[11],
                            'date_returned': line[12],
                            'transfer_exception_type_id': line[13],
                            'reference': line[14],
                            'stock_transfer_order_id': line[15],
                            'location_src_id': line[16],
                            'location_dest_id': line[17],
                            'return_location_id': line[18],
                        })
                        if values.get("transfer_order_type_id") != "":
                            res_id = 0
                        line_values.update({
                            'product_id': line[19],
                            'name': line[20],
                            'project_id': line[21],
                            'site_type': line[22],
                            'tower_height': line[23],
                            'kpa': line[24],
                            'wind_zone': line[25],
                            'delivered_qty': line[26],
                            'remaining_qty': line[27],
                            'product_uom': line[28],
                            'supplier_id': line[29],
                            'product_uom_qty': line[30],
                            'date_scheduled': line[31],
                            'location_src_id': line[32],
                            'location_dest_id': line[33],
                        })
                        if values.get("transfer_order_type_id") != "":
                            res = material.create_transfer_order(values)
                            res_id = res.id
                            res_line = material.create_transfer_order_line(line_values, res_id)
                        elif values.get("product_id") != "":
                            res_line = material.create_transfer_order_line(line_values, res_id)

            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                line_values = dict(zip(keys, field))

                if values:
                    if i == 0:
                        continue
                    else:

                        values.update({
                                'partner_id': field[0],
                                'transfer_order_type_id' : field[1],
                                'user_id' : field[2],
                                'transfer_order_category_id' : field[3],
                                'company_id'  : field[4],
                                'purchase_id'  : field[5],
                                'transporter_id': field[6],
                                'date_request': field[7],
                                'date_order': field[8],
                                'date_scheduled': field[9],
                                'delivery_deadline': field[10],
                               'date_delivered': field[11],
                               'date_returned': field[12],
                              'transfer_exception_type_id': field[13],
                              'reference': field[14],
                              'stock_transfer_order_id': field[15],
                              'location_src_id': field[16],
                              'location_dest_id': field[17],
                              'return_location_id': field[18],
                        })
                        if values.get("transfer_order_type_id") != "":
                            res_id = 0
                        line_values.update({
                            'product_id': field[19],
                            'name': field[20],
                            'project_id': field[21],
                            'site_type': field[22],
                            'tower_height': field[23],
                            'kpa': field[24],
                            'wind_zone': field[25],
                            'delivered_qty': field[26],
                            'remaining_qty': field[27],
                            'product_uom': field[28],
                            'supplier_id': field[29],
                            'product_uom_qty': field[30],
                            'date_scheduled': field[31],
                            'location_src_id': field[32],
                            'location_dest_id': field[33],
                        })
                        if values.get("transfer_order_type_id") != "":
                            res = material.create_transfer_order(values)
                            res_id = res.id
                            res_line = material.create_transfer_order_line( line_values , res_id)
                        elif values.get("product_id") != "":
                            res_line = material.create_transfer_order_line(line_values, res_id)
            material.user_id = self.env.user
            material.is_processed = True
            material.un_processed = False
    
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
        partner = self.find_transporter(values.get('partner_id'))
        exception = self.find_transfer_exception(values.get('transfer_exception_type_id'))
        transfero = self.find_transfer_order(values.get('stock_transfer_order_id'))
        loc_src = self.find_destination_location(values.get('location_src_id'))
        dest_loc = self.find_destination_location(values.get('location_dest_id'))
        return_loc = self.find_destination_location(values.get('return_location_id'))
        date_request = fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_order = fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_schedule = fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        delivery_date = fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # if values.get('date_request') :
        #     date_request = datetime.strptime(values.get('date_request'), '%Y-%m-%d %H:%M:%S')
        # if values.get('date_order') :
        #     date_order = datetime.strptime(values.get('date_order'), '%Y-%m-%d %H:%M:%S')
        # if values.get('date_scheduled') :
        #     date_schedule = datetime.strptime(values.get('date_scheduled'), '%Y-%m-%d %H:%M:%S')
        # if values.get('delivery_deadline') :
        #     delivery_date = datetime.strptime(values.get('delivery_deadline'), '%Y-%m-%d %H:%M:%S')





        transfer_order = self.env['stock.transfer.order']

        data =  {
                'partner_id': partner.id if partner else False,
                'transfer_order_type_id' : transfer_type.id,
                'sequence_code': transfer_type.code,
                'user_id' : user_id.id,
                'transfer_order_category_id':category.id,
                'company_id':company.id,
                'purchase_id':purchase_order.id if purchase_order else False,
                'transporter_id':transporter.id if transporter else False,
                'transfer_exception_type_id': exception.id if exception else False,
                 'stock_transfer_order_id': transfero.id if transfero else False ,
                 'location_src_id': loc_src.id if loc_src else False,
                 'location_dest_id': dest_loc.id if dest_loc else False,
                 'return_location_id': return_loc.id if return_loc else False,
                 'date_request': date_request,
                 'date_order':  date_order,
                  'date_scheduled': date_schedule,
                  'delivery_deadline': delivery_date,
                  'date_delivered': values.get('date_delivered') if values.get('date_delivered') else ' ',
                  'date_returned': values.get('date_returned') if values.get('date_returned') else ' ',
                  'reference': values.get('reference') if values.get('reference') else ' ' ,
                }

        torder = transfer_order.create(data)
        
        return torder

    def create_transfer_order_line(self, line_values, rec_id):

        if line_values.get("product_id") == "":
            raise UserError(_('Product field cannot be empty.'))

        if line_values.get("location_src_id") == "":
            raise UserError(_('Source Location field cannot be empty.'))

        if line_values.get("location_dest_id") == "":
            raise UserError(_('Destination field cannot be empty.'))



        product = self.find_product(line_values.get('product_id'))
        source_location = self.find_source_location(line_values.get('location_src_id'))
        dest_location = self.find_destination_location(line_values.get('location_dest_id'))
        supplier = self.find_transporter(line_values.get('supplier_id'))
        project = self.find_project(line_values.get('project_id'))
        produc_uom = self.find_product_uom(line_values.get('product_uom'))

        transfer_order_line = self.env['stock.transfer.order.line']

        data = {
            'product_id': product.id,
            'name': line_values.get("name"),
            'product_uom_qty': line_values.get("product_uom_qty"),
            # 'date_scheduled': line_values.get("date_scheduled"),
            'location_src_id': source_location.id,
            'location_dest_id': dest_location.id,
            'stock_transfer_order_id': rec_id,
            'project_id': project.id if project else False,
            'product_uom': produc_uom.id if produc_uom else False,
            'supplier_id': supplier.id if supplier else False,
            'kpa': line_values.get('kpa') if line_values.get('kpa') else 0,
            'site_type': line_values.get('site_type') if line_values.get('site_type') else 0 ,
            'tower_height': line_values.get('tower_height') if line_values.get('tower_height') else 0,
            'wind_zone': line_values.get('wind_zone') if line_values.get('wind_zone') else 0 ,
            'delivered_qty': line_values.get('delivered_qty') if line_values.get('delivered_qty') else 0 ,
            'remaining_qty': line_values.get('remaining_qty') if line_values.get('remaining_qty') else 0 ,

        }

        order_line = transfer_order_line.create(data)
        return order_line


    def create_return_line(self, line_values, rec_id):

        if line_values.get("product_id") == "":
            raise UserError(_('Return Product field cannot be empty.'))

        if line_values.get("location_src_id") == "":
            raise UserError(_('Return Source Location field cannot be empty.'))

        if line_values.get("location_dest_id") == "":
            raise UserError(_('Return Destination field cannot be empty.'))



        product = self.find_product(line_values.get('product_id'))
        source_location = self.find_source_location(line_values.get('location_src_id'))
        dest_location = self.find_destination_location(line_values.get('location_dest_id'))
        supplier = self.find_transporter(line_values.get('supplier_id'))
        project = self.find_project(line_values.get('project_id'))
        produc_uom = self.find_product_uom(line_values.get('product_uom'))

        return_order_line = self.env['stock.transfer.return.line']

        data = {
            'product_id': product.id,
            'name': line_values.get("name"),
            'product_uom_qty': line_values.get("product_uom_qty"),
            'date_scheduled': line_values.get("date_scheduled"),
            'location_src_id': source_location.id,
            'location_dest_id': dest_location.id,
            'stock_transfer_order_id': rec_id,
            'project_id': project.id if project else False,
            'product_uom': produc_uom.id if produc_uom else False,
            'supplier_id': supplier.id if supplier else False,
            'received_qty': line_values.get('delivered_qty') if line_values.get('delivered_qty') else 0 ,
            'remaining_qty': line_values.get('remaining_qty') if line_values.get('remaining_qty') else 0 ,

        }

        return_order_line = return_order_line.create(data)
        return return_order_line



    def find_project(self, project):
        get_project = self.env['project.project'].search([('name','=', project)], limit=1)
        return get_project

    def find_product_uom(self, uom):
        prod_uom = self.env['uom.uom'].search([('name','=', uom)], limit=1)
        return prod_uom

    def find_product(self, product):
        product_line = self.env['product.product']
        transfer_search = product_line.search([('name', '=', product)], limit=1)
        if transfer_search:
            return transfer_search
        else:
            raise UserError(_('Field Product is not correctly set.'))

    def find_transfer_exception(self, exception):
        exception = self.env['stock.transfer.exception.type'].search([('name','=',exception)], limit=1)
        return exception

    def find_transfer_order(self, picking):
        picking = self.env['stock.picking'].search([('name','=',picking)], limit=1)
        return picking

    def find_source_location(self, src_location):
        src_loc = self.env['stock.location']
        src_loc_search = src_loc.search([('name', '=', src_location)], limit=1)
        if src_loc_search:
            return src_loc_search
        else:
            raise UserError(_('Field Source Location is not correctly set.'))

    def find_destination_location(self, dest_location):
        dest_loc = self.env['stock.location']
        dest_loc_search = dest_loc.search([('name', '=', dest_location)], limit=1)
        if dest_loc_search:
            return dest_loc_search
        else:
            raise UserError(_('Field Destination Location is not correctly set.'))

    def find_transfer_type(self,type):
        transfer_type =self.env['stock.transfer.order.type']
        transfer_search = transfer_type.search([('name','=',type)], limit=1)
        if transfer_search:
            return transfer_search
        else:
            raise UserError(_('Field Transfer Type is not correctly set.'))
    
        
    def find_requested_owner(self,user):
        request_user =self.env['res.users']
        user_search = request_user.search([('partner_id.name','=',user)], limit=1)
        if user_search:
            return user_search
        else:
            raise UserError(_('Field Requested Owner is not correctly set.'))
    
        
    def find_transfer_category(self,category):
        request_category =self.env['stock.transfer.order.category']
        category_search = request_category.search([('name','=',category)], limit=1)
        if category_search:
            return category_search
        else:
            raise UserError(_('Field Transfer Category is not correctly set.'))
    
        
    def find_company(self,company):
        rquest_company =self.env['res.company']
        company_search = rquest_company.search([('name','=',company)], limit=1)
        if company_search:
            return company_search
        else:
            raise UserError(_('Field Comapany is not correctly set.'))
    

    def find_purchase_order(self,purchase):
        purchase_order =self.env['purchase.order']
        order_search = purchase_order.search([('name','=',purchase)], limit=1)
        return order_search

    
    def find_transporter(self,transporter):
        request_transporter =self.env['res.partner']
        transporter_search = request_transporter.search([('name','=',transporter)], limit=1)
        return transporter_search

