# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import csv
import base64
import xlrd
from odoo.tools import ustr
from datetime import date, datetime, timedelta
from dateutil import parser

import logging

_logger = logging.getLogger(__name__)


class ImportLotSerialWizard(models.TransientModel):
    _name = "sh.import.lot.serial.picking"
    _description = "Import lot or serial number wizard"

    import_type = fields.Selection([
        ('csv', 'CSV File'),
        ('excel', 'Excel File')
    ], default="csv", string="Import File Type", required=True)
    file = fields.Binary(string="File", required=True)
    lot_type = fields.Selection([('lot', 'Lot'), ('serial', 'Serial')],
                                default='lot', string='Lot/Serial Type', required=True)
    is_create_lot = fields.Boolean("Create Lot/Serial ?")
    display_is_create_lot = fields.Boolean('Display Is Create Lot/Serial',default=False)

    def validate_field_value(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        """ Validate field value, depending on field type and given value """
        self.ensure_one()

        try:
            checker = getattr(self, 'validate_field_' + field_ttype)
        except AttributeError:
            _logger.warning(
                field_ttype + ": This type of field has no validation method")
            return {}
        else:
            return checker(field_name, field_ttype, field_value, field_required, field_name_m2o)

    def validate_field_many2many(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            name_relational_model = self.env['stock.move.line'].fields_get()[
                field_name]['relation']

            ids_list = []
            if field_value.strip() not in (None, ""):
                for x in field_value.split(','):
                    x = x.strip()
                    if x != '':
                        record = self.env[name_relational_model].sudo().search([
                            (field_name_m2o, '=', x)
                        ], limit=1)

                        if record:
                            ids_list.append(record.id)
                        else:
                            return {"error": " - " + x + " not found. "}
                            break

            return {field_name: [(6, 0, ids_list)]}

    def validate_field_many2one(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            name_relational_model = self.env['stock.move.line'].fields_get()[
                field_name]['relation']
            record = self.env[name_relational_model].sudo().search([
                (field_name_m2o, '=', field_value)
            ], limit=1)
            return {field_name: record.id if record else False}

    def validate_field_text(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_integer(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_float(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_char(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_boolean(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        boolean_field_value = False
        if field_value.strip() == 'TRUE':
            boolean_field_value = True

        return {field_name: boolean_field_value}

    def validate_field_selection(self, field_name, field_ttype, field_value, field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}

        #get selection field key and value.
        selection_key_value_list = self.env['stock.move.line'].sudo(
        )._fields[field_name].selection
        if selection_key_value_list and field_value not in (None, ""):
            for tuple_item in selection_key_value_list:
                if tuple_item[1] == field_value:
                    return {field_name: tuple_item[0] or False}

            return {"error": " - " + field_name + " given value " + str(field_value) + " does not match for selection. "}

        #finaly return false
        if field_value in (None, ""):
            return {field_name: False}

        return {field_name: field_value or False}

    def show_success_msg(self, counter, skipped_line_no):
        #open the new success message box
        view = self.env.ref('sh_message.sh_message_wizard')
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k, v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg

        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    @api.model
    def default_get(self, fields_list):
        res = super(ImportLotSerialWizard, self).default_get(fields_list)
        move_id = self.env['stock.move'].sudo().browse(
                self.env.context.get('active_id'))
        if move_id.picking_id.picking_type_id.code == 'incoming':
            res.update({
                'display_is_create_lot':True
                })
        return res

    def import_lot_serial_apply(self):
        stock_move_lie_obj = self.env['stock.move.line']
        ir_model_fields_obj = self.env['ir.model.fields']
        if self and self.file:
            move_id = self.env['stock.move'].sudo().browse(
                self.env.context.get('active_id'))
            if move_id.move_line_ids:
                move_id.move_line_ids.unlink()
                move_id._action_confirm(merge=True, merge_into=False)
            # For CSV
            if self.import_type == 'csv':
                counter = 1
                skipped_line_no = {}
                row_field_dic = {}
                row_field_error_dic = {}
                try:
                    file = str(base64.decodebytes(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header = True
                    for row in myreader:
                        try:
                            if skip_header:
                                skip_header = False
                                for i in range(2, len(row)):
                                    name_field = row[i]
                                    name_m2o = False
                                    if '@' in row[i]:
                                        list_field_str = name_field.split('@')
                                        name_field = list_field_str[0]
                                        name_m2o = list_field_str[1]
                                    search_field = ir_model_fields_obj.sudo().search([
                                        ("model", "=", "stock.move.line"),
                                        ("name", "=", name_field),
                                        ("store", "=", True),
                                    ], limit=1)
                                    if search_field:
                                        field_dic = {
                                            'name': name_field,
                                            'ttype': search_field.ttype,
                                            'required': search_field.required,
                                            'name_m2o': name_m2o
                                        }
                                        row_field_dic.update({i: field_dic})
#                                     else:
#                                         row_field_error_dic.update(
#                                             {row[i]: " - field not found"})
                                counter = counter + 1
                                continue
                            if row_field_error_dic:
                                res = self.show_success_msg(
                                    0, row_field_error_dic)
                                return res
                            if row[0] != '':
                                vals = {}
                                if self.lot_type == 'lot':
                                    if move_id.product_id.tracking == 'lot':
                                        if move_id.picking_id.picking_type_id.code == 'incoming':
                                            if row[0] != '':
                                                vals.update({
                                                    'lot_name': row[0],
                                                })
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                counter = counter + 1
                                                continue
                                            if row[1] != '':
                                                vals.update({
                                                    'qty_done': float(row[1]),
                                                    
                                                })
                                            else:
                                                vals.update({
                                                    'qty_done': 0.0,
                                                })
                                                
                                            if row[2] != '':
                                                wtystart = parser.parse(row[2])
                                                wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_start': wty_start_date,
                                                    
                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_start': False,
                                                }) 
                                            if row[3] != '':
                                                wtyend = parser.parse(row[3])
                                                wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_end': wty_end_date,
                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_end': False,
                                                })     
                                        elif move_id.picking_id.picking_type_id.code == 'outgoing' or move_id.picking_id.picking_type_id.code == 'internal':
                                            if self.is_create_lot:
                                                if row[0] != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',row[0])],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        lot_id = self.env['stock.production.lot'].sudo().create({
                                                            'name':row[0],
                                                            'product_id':move_id.product_id.id,
                                                            'company_id':move_id.company_id.id,
                                                            })
                                                        if lot_id:
                                                            vals.update({
                                                                'lot_id': lot_id.id,
                                                            })
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue       
                                                if row[1] != '':
                                                    vals.update({
                                                        'qty_done': float(row[1]),
                                                    })
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if row[2] != '':
                                                    wtystart = parser.parse(row[2])
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 
                                                
                                                if row[3] != '':
                                                    wtyend = parser.parse(row[3])
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })     
                                            else:
                                                if row[0] != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',row[0])],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        skipped_line_no[str(
                                                        counter)] = " - Lot/Serial not found. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if row[1] != '':
                                                    vals.update({
                                                        'qty_done': float(row[1]),
                                                    })
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                if row[2] != '':
                                                    wtystart = parser.parse(row[2])
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 
                                                
                                                if row[3] != '':
                                                    wtyend = parser.parse(row[3])
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    }) 
                                                
                                    else:
                                        raise UserError(
                                            "Product must be tracking as lot.")
                                elif self.lot_type == 'serial':
                                    if move_id.product_id.tracking == 'serial':
                                        if move_id.picking_id.picking_type_id.code == 'incoming':
                                            if row[0] != '':
                                                vals.update({
                                                    'lot_name': row[0],
                                                })
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                counter = counter + 1
                                                continue
                                            if row[1] != '':
                                                if int(row[1]) == 1:
                                                    vals.update({
                                                        'qty_done': float(row[1]),
                                                    })
                                                elif int(row[1]) > 1:
                                                    skipped_line_no[str(
                                                        counter)] = " Quantity must be equal to one for import serial numbers. "
                                                    counter = counter + 1
                                                    continue
                                                         
                                            else:
                                                vals.update({
                                                    'qty_done': 0.0,
                                                })
                                                
                                            if row[2] != '':
                                                wtystart = parser.parse(row[2])
                                                wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                            else:
                                                vals.update({
                                                    'warranty_date_start': False,
                                                    }) 
                                                
                                            if row[3] != '':
                                                wtyend = parser.parse(row[3])
                                                wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_end': wty_end_date,
                                                    })
                                            else:
                                                vals.update({
                                                     'warranty_date_end': False,
                                                })    
                                        elif move_id.picking_id.picking_type_id.code == 'outgoing' or move_id.picking_id.picking_type_id.code == 'internal':
                                            if self.is_create_lot:
                                                if row[0] != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',row[0])],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        lot_id = self.env['stock.production.lot'].sudo().create({
                                                                'name':row[0],
                                                                'product_id':move_id.product_id.id,
                                                                'company_id':move_id.company_id.id,
                                                                })
                                                        if lot_id:
                                                            vals.update({
                                                                'lot_id': lot_id.id,
                                                            })
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if row[1] != '':
                                                    if int(row[1]) == 1:
                                                        vals.update({
                                                            'qty_done': float(row[1]),
                                                        })
                                                    elif int(row[1]) > 1:
                                                        skipped_line_no[str(
                                                            counter)] = " Quantity must be equal to one for import serial numbers. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if row[2] != '':
                                                    wtystart = parser.parse(row[2])
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 
                                                
                                                if row[3] != '':
                                                    wtyend = parser.parse(row[3])
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })     
                                            else:
                                                if row[0] != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',row[0])],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        skipped_line_no[str(
                                                        counter)] = " - Lot/Serial not found. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if row[1] != '':
                                                    if int(row[1]) == 1:
                                                        vals.update({
                                                            'qty_done': float(row[1]),
                                                        })
                                                    elif int(row[1]) > 1:
                                                        skipped_line_no[str(
                                                            counter)] = " Quantity must be equal to one for import serial numbers. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if row[2] != '':
                                                    wtystart = parser.parse(row[2])
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 
                                                
                                                if row[3] != '':
                                                    wtyend = parser.parse(row[3])
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })     
                                                 
                                    else:
                                        raise UserError(
                                            "Product must be tracking as serial.")
                                vals.update({
                                    'product_id': move_id.product_id.id,
                                    'picking_id': move_id.picking_id.id,
                                    'move_id': move_id.id,
                                    'product_uom_id': move_id.product_uom.id,
                                    'location_id': move_id.location_id.id,
                                    'location_dest_id': move_id.location_dest_id.id,
                                })
                                is_any_error_in_dynamic_field = False
                                for k_row_index, v_field_dic in row_field_dic.items():
    
                                    field_name = v_field_dic.get("name")
                                    field_ttype = v_field_dic.get("ttype")
                                    field_value = row[k_row_index]
                                    field_required = v_field_dic.get(
                                        "required")
                                    field_name_m2o = v_field_dic.get(
                                        "name_m2o")
    
                                    dic = self.validate_field_value(
                                        field_name, field_ttype, field_value, field_required, field_name_m2o)
                                    if dic.get("error", False):
                                        skipped_line_no[str(counter)] = dic.get(
                                            "error")
                                        is_any_error_in_dynamic_field = True
                                        break
                                    else:
                                        vals.update(dic)
                                if is_any_error_in_dynamic_field:
                                    counter = counter + 1
                                    continue
                                stock_move_lie_obj.sudo().create(vals)
                                counter = counter + 1

                            else:
                                skipped_line_no[str(
                                    counter)] = " - Lot/Serial is empty. "
                                counter = counter + 1

                        except Exception as e:
                            skipped_line_no[str(
                                counter)] = " - Value is not valid " + ustr(e)
                            counter = counter + 1
                            continue

                except Exception:
                    raise UserError(
                        _("Sorry, Your csv file does not match with our format"))

                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(
                        completed_records, skipped_line_no)
                    return res

            # For Excel
            if self.import_type == 'excel':
                counter = 1
                skipped_line_no = {}
                row_field_dic = {}
                row_field_error_dic = {}
                try:
                    wb = xlrd.open_workbook(
                        file_contents=base64.decodebytes(self.file))
                    sheet = wb.sheet_by_index(0)
                    skip_header = True
                    for row in range(sheet.nrows):
                        try:
                            if skip_header:
                                skip_header = False
                                for i in range(2, sheet.ncols):
                                    name_field = sheet.cell(row, i).value
                                    name_m2o = False
                                    if '@' in sheet.cell(row, i).value:
                                        list_field_str = name_field.split('@')
                                        name_field = list_field_str[0]
                                        name_m2o = list_field_str[1]
                                    search_field = ir_model_fields_obj.sudo().search([
                                        ("model", "=", "stock.move.line"),
                                        ("name", "=", name_field),
                                        ("store", "=", True),
                                    ], limit=1)
                                    if search_field:
                                        field_dic = {
                                            'name': name_field,
                                            'ttype': search_field.ttype,
                                            'required': search_field.required,
                                            'name_m2o': name_m2o
                                        }
                                        row_field_dic.update({i: field_dic})
#                                     else:
#                                         row_field_error_dic.update(
#                                             {sheet.cell(row, i).value: " - field not found"})
                                counter = counter + 1
                                continue
                            if row_field_error_dic:
                                res = self.show_success_msg(
                                    0, row_field_error_dic)
                                return res

                            if sheet.cell(row, 0).value != '':
                                vals = {}
                                if self.lot_type == 'lot':
                                    if move_id.product_id.tracking == 'lot':
                                        if move_id.picking_id.picking_type_id.code == 'incoming':
                                            if sheet.cell(row, 0).value != '':
                                                vals.update({
                                                    'lot_name': sheet.cell(row, 0).value,
                                                })
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                counter = counter + 1
                                                continue
                                            if sheet.cell(row, 1).value != '':
                                                vals.update({
                                                    'qty_done': float(sheet.cell(row, 1).value),
                                                })
                                            else:
                                                vals.update({
                                                    'qty_done': 0.0,
                                                })
                                            if sheet.cell(row, 2).value != '':
                                                wtystart = parser.parse(sheet.cell(row, 2).value)
                                                wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_start': wty_start_date,

                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_start': False,
                                                }) 
                                                
                                            if sheet.cell(row, 3).value != '':
                                                wtyend = parser.parse(sheet.cell(row, 3).value)
                                                wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_end': wty_end_date,
                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_end': False,
                                                })     
                                        elif move_id.picking_id.picking_type_id.code == 'outgoing' or move_id.picking_id.picking_type_id.code == 'internal':
                                            if self.is_create_lot:
                                                if sheet.cell(row, 0).value != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',sheet.cell(row, 0).value)],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        lot_id = self.env['stock.production.lot'].sudo().create({
                                                            'name':sheet.cell(row, 0).value,
                                                            'product_id':move_id.product_id.id,
                                                            'company_id':move_id.company_id.id,
                                                            })
                                                        if lot_id:
                                                            vals.update({
                                                                'lot_id': lot_id.id,
                                                            })
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue       
                                                if sheet.cell(row, 1).value != '':
                                                    vals.update({
                                                        'qty_done': float(sheet.cell(row, 1).value),
                                                    })
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                if sheet.cell(row, 2).value != '':
                                                    wtystart = parser.parse(sheet.cell(row, 2).value)
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 

                                                if sheet.cell(row, 3).value != '':
                                                    wtyend = parser.parse(sheet.cell(row, 3).value)
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })         

                                            else:
                                                if sheet.cell(row, 0).value != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',sheet.cell(row, 0).value)],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        skipped_line_no[str(
                                                        counter)] = " - Lot/Serial not found. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if sheet.cell(row, 1).value != '':
                                                    vals.update({
                                                        'qty_done': float(sheet.cell(row, 1).value),
                                                    })
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if sheet.cell(row, 2).value != '':
                                                    wtystart = parser.parse(sheet.cell(row, 2).value)
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 

                                                if sheet.cell(row, 3).value != '':
                                                    wtyend = parser.parse(sheet.cell(row, 3).value)
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })         
                                    else:
                                        raise UserError(
                                            "Product must be tracking as lot.")
                                elif self.lot_type == 'serial':
                                    if move_id.product_id.tracking == 'serial':
                                        if move_id.picking_id.picking_type_id.code == 'incoming':
                                            if sheet.cell(row, 0).value != '':
                                                vals.update({
                                                    'lot_name': sheet.cell(row, 0).value,
                                                })
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                counter = counter + 1
                                                continue
                                            if sheet.cell(row, 1).value != '':
                                                if int(sheet.cell(row, 1).value) == 1:
                                                    vals.update({
                                                        'qty_done': float(sheet.cell(row, 1).value),
                                                    })
                                                elif int(sheet.cell(row, 1).value) > 1:
                                                    skipped_line_no[str(
                                                        counter)] = " Quantity must be equal to one for import serial numbers. "
                                                    counter = counter + 1
                                                    continue
                                            else:
                                                vals.update({
                                                    'qty_done': 0.0,
                                                })
                                                
                                            if sheet.cell(row, 2).value != '':
                                                wtystart = parser.parse(sheet.cell(row, 2).value)
                                                wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_start': wty_start_date,

                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_start': False,
                                                }) 
                                                
                                            if sheet.cell(row, 3).value != '':
                                                wtyend = parser.parse(sheet.cell(row, 3).value)
                                                wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                vals.update({
                                                    'warranty_date_end': wty_end_date,
                                                })
                                            else:
                                                vals.update({
                                                    'warranty_date_end': False,
                                                })   
                                                
                                        elif move_id.picking_id.picking_type_id.code == 'outgoing' or move_id.picking_id.picking_type_id.code == 'internal':
                                            if self.is_create_lot:
                                                if sheet.cell(row, 0).value != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',sheet.cell(row, 0).value)],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        lot_id = self.env['stock.production.lot'].sudo().create({
                                                                'name':sheet.cell(row, 0).value,
                                                                'product_id':move_id.product_id.id,
                                                                'company_id':move_id.company_id.id,
                                                                })
                                                        if lot_id:
                                                            vals.update({
                                                                'lot_id': lot_id.id,
                                                            })
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if sheet.cell(row, 1).value != '':
                                                    if int(sheet.cell(row, 1).value) == 1:
                                                        vals.update({
                                                            'qty_done': float(sheet.cell(row, 1).value),
                                                        })
                                                    elif int(sheet.cell(row, 1).value) > 1:
                                                        skipped_line_no[str(
                                                            counter)] = " Quantity must be equal to one for import serial numbers. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if sheet.cell(row, 2).value != '':
                                                    wtystart = parser.parse(sheet.cell(row, 2).value)
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 

                                                if sheet.cell(row, 3).value != '':
                                                    wtyend = parser.parse(sheet.cell(row, 3).value)
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })         
                                            else:
                                                if sheet.cell(row, 0).value != '':
                                                    lot_id = self.env['stock.production.lot'].sudo().search([('name','=',row[0])],limit=1)
                                                    if lot_id:
                                                        vals.update({
                                                            'lot_id': lot_id.id,
                                                        })
                                                    else:
                                                        skipped_line_no[str(
                                                        counter)] = " - Lot/Serial not found. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    skipped_line_no[str(
                                                    counter)] = " - Lot/Serial not found. "
                                                    counter = counter + 1
                                                    continue
                                                if sheet.cell(row, 1).value != '':
                                                    if int(sheet.cell(row, 1).value) == 1:
                                                        vals.update({
                                                            'qty_done': float(sheet.cell(row, 1).value),
                                                        })
                                                    elif int(sheet.cell(row, 1).value) > 1:
                                                        skipped_line_no[str(
                                                            counter)] = " Quantity must be equal to one for import serial numbers. "
                                                        counter = counter + 1
                                                        continue
                                                else:
                                                    vals.update({
                                                        'qty_done': 0.0,
                                                    })
                                                    
                                                if sheet.cell(row, 2).value != '':
                                                    wtystart = parser.parse(sheet.cell(row, 2).value)
                                                    wty_start_date = wtystart.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_start': wty_start_date,

                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_start': False,
                                                    }) 

                                                if sheet.cell(row, 3).value != '':
                                                    wtyend = parser.parse(sheet.cell(row, 3).value)
                                                    wty_end_date = wtyend.strftime("%Y-%m-%d")
                                                    vals.update({
                                                        'warranty_date_end': wty_end_date,
                                                    })
                                                else:
                                                    vals.update({
                                                        'warranty_date_end': False,
                                                    })         
                                                 
                                    else:
                                        raise UserError(
                                            "Product must be tracking as serial.")
                                
                                vals.update({
                                    'product_id': move_id.product_id.id,
                                    'picking_id': move_id.picking_id.id,
                                    'move_id': move_id.id,
                                    'product_uom_id': move_id.product_uom.id,
                                    'location_id': move_id.location_id.id,
                                    'location_dest_id': move_id.location_dest_id.id,
                                })
                                is_any_error_in_dynamic_field = False
                                for k_row_index, v_field_dic in row_field_dic.items():

                                    field_name = v_field_dic.get("name")
                                    field_ttype = v_field_dic.get("ttype")
                                    field_value = sheet.cell(
                                        row, k_row_index).value
                                    field_required = v_field_dic.get(
                                        "required")
                                    field_name_m2o = v_field_dic.get(
                                        "name_m2o")

                                    dic = self.validate_field_value(
                                        field_name, field_ttype, field_value, field_required, field_name_m2o)
                                    if dic.get("error", False):
                                        skipped_line_no[str(counter)] = dic.get(
                                            "error")
                                        is_any_error_in_dynamic_field = True
                                        break
                                    else:
                                        vals.update(dic)

                                if is_any_error_in_dynamic_field:
                                    counter = counter + 1
                                    continue
                                stock_move_lie_obj.sudo().create(vals)
                                counter = counter + 1

                            else:
                                skipped_line_no[str(
                                    counter)] = " - Lot/Serial is empty. "
                                counter = counter + 1

                        except Exception as e:
                            skipped_line_no[str(
                                counter)] = " - Value is not valid " + ustr(e)
                            counter = counter + 1
                            continue

                except Exception:
                    raise UserError(
                        _("Sorry, Your excel file does not match with our format"))

                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(
                        completed_records, skipped_line_no)
                    return res
