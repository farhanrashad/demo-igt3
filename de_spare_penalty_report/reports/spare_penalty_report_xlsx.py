import json
from odoo import models
from odoo.exceptions import UserError
from datetime import datetime


class GenerateXLSXReport(models.Model):
    _name = 'report.de_spare_penalty_report.spare_penalty_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Spare Penalty Report XLSX"

    def generate_xlsx_report(self, workbook, data, lines):
        start_date = data['start_date']
        end_date = data['end_date']
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        start_date = start_date.strftime("%Y/%m/%d")
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime("%Y/%m/%d")
        
        
        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Spare Penalty Report')
        
        sheet.write(3, 0, 'mrf_number', format1)
        sheet.write(3, 1, 'mrf_type', format1)
        sheet.write(3, 2, 'requestor', format1)
        sheet.write(3, 3, 'supplier', format1)
        sheet.write(3, 4, 'submission_date', format1)
        sheet.write(3, 5, 'pick_up_date', format1)
        sheet.write(3, 6, 'penalty_effective_date', format1)
        sheet.write(3, 7, 'create_date', format1)
        sheet.write(3, 8, 'site', format1)
        sheet.write(3, 9, 'on_air', format1)
        sheet.write(3, 10, 'asset', format1)
        sheet.write(3, 11, 'product_code', format1)
        sheet.write(3, 12, 'lifetime', format1)
        sheet.write(3, 13, 'usedlife', format1)
        sheet.write(3, 14, 'remaininglife', format1)
        sheet.write(3, 15, 'deliver', format1)
        sheet.write(3, 16, 'return', format1)
        sheet.write(3, 17, 'quantity', format1)
        sheet.write(3, 18, 'product_cost', format1)
        sheet.write(3, 19, 'penalty', format1)
        sheet.write(3, 20, 'backcharged', format1)
        sheet.write(3, 21, 'total', format1)
        sheet.write(3, 22, 'returned', format1)
        sheet.write(3, 23, 'remark', format1)
        
        
        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter'})
        row = 4
        sheet.set_column(row, 0, 50)
        sheet.set_column(row, 1, 20)
        sheet.set_column(row, 2, 20)
        sheet.set_column(row, 3, 20)
        sheet.set_column(row, 4, 20)
        sheet.set_column(row, 5, 20)
        sheet.set_column(row, 6, 20)
        sheet.set_column(row, 7, 20)
        sheet.set_column(row, 8, 20)
        sheet.set_column(row, 9, 20)
        sheet.set_column(row, 10, 20)
        sheet.set_column(row, 11, 20)
        sheet.set_column(row, 12, 20)
        sheet.set_column(row, 13, 20)
        sheet.set_column(row, 14, 20)
        sheet.set_column(row, 15, 20)
        sheet.set_column(row, 16, 20)
        sheet.set_column(row, 17, 20)
        sheet.set_column(row, 18, 20)
        sheet.set_column(row, 19, 20)
        sheet.set_column(row, 20, 20)
        sheet.set_column(row, 21, 20)
        sheet.set_column(row, 22, 20)
        sheet.set_column(row, 23, 20)
        
        order_ids = self.env['stock.transfer.order'].search([('date_order','>=',data['start_date']),('date_order','<=',data['end_date'])])
        
        try:
            for id in lines:
                if id.name:
                    mrf_number = id.name
                else:
                    mrf_number = None

                if id.transfer_order_type_id:
                    type = id.transfer_order_type_id.name
                else:
                    type = None

                if id.user_id:
                    requestor = id.user_id.name
                else:
                    requestor = None
                if id.delivery_deadline:
                   submission_date = id.delivery_deadline.strftime("%d/%m/%Y")
                else:
                    submission_date = None

                if id.date_request:
                   pick_up_date = id.date_request.strftime("%d/%m/%Y")
                else:
                    pick_up_date = None

                if id.date_order:
                    create_date = id.date_order.strftime("%d/%m/%Y")
                else:
                    create_date = None

                if id.date_delivered:
                    deliver = id.date_delivered.strftime("%d/%m/%Y")
                else:
                    deliver = None

                if id.return_deadline:
                    return_deadline = id.return_deadline.strftime("%d/%m/%Y")
                else:
                    return_deadline = None

                supplier = None
                site = None
                product_code = None
                product_qty = None
                if id.stock_transfer_order_line:
                    for line in id.stock_transfer_order_line:
                        if line.supplier_id:
                            supplier = line.supplier_id.name
                        else:
                            supplier = None

                        if line.project_id:
                            site = line.project_id.name
                        else:
                            site = None

                        if line.product_id.default_code:
                            product_code = product.product_id.default_code
                        else:
                            product_code = None

                        if line.delivered_qty:
                            product_qty = line.delivered_qty
                        else:
                            product_qty = None


                        sheet.write(row, 0, mrf_number, format2)
                        sheet.write(row, 1, type, format2)
                        sheet.write(row, 2, requestor, format2)
                        sheet.write(row, 3, supplier, format2)
                        sheet.write(row, 4, submission_date, format2)
                        sheet.write(row, 5, pick_up_date, format2)
                        #sheet.write(row, 6, penalty_effective_date, format2)
                        sheet.write(row, 7, create_date, format2)
                        sheet.write(row, 8, site, format2)
                        #sheet.write(row, 9, on_air, format2)
                        #sheet.write(row, 10, asset, format2)
                        sheet.write(row, 11, product_code, format2)
                        #sheet.write(row, 12, life_time, format2)
                        #sheet.write(row, 13, used_life, format2)
                        #sheet.write(row, 14, remaining_life, format2)
                        sheet.write(row, 15, deliver, format2)
                        sheet.write(row, 16, return_deadline, format2)
                        sheet.write(row, 17, product_qty, format2)
                        #sheet.write(row, 18, product_cost, format2)
                        #sheet.write(row, 19, amount, format2)
                        #sheet.write(row, 20, back_charged, format2)
                        #sheet.write(row, 21, total, format2)
                        #sheet.write(row, 22, returned, format2)
                        #sheet.write(row, 23, remark, format2)

                        row = row + 1
                else:
                    sheet.write(row, 0, mrf_number, format2)
                    sheet.write(row, 1, type, format2)
                    sheet.write(row, 2, requestor, format2)
                    sheet.write(row, 3, supplier, format2)
                    sheet.write(row, 4, submission_date, format2)
                    sheet.write(row, 5, pick_up_date, format2)
                    #sheet.write(row, 6, penalty_effective_date, format2)
                    sheet.write(row, 7, create_date, format2)
                    sheet.write(row, 8, site, format2)
                    #sheet.write(row, 9, on_air, format2)
                    #sheet.write(row, 10, asset, format2)
                    sheet.write(row, 11, product_code, format2)
                    #sheet.write(row, 12, life_time, format2)
                    #sheet.write(row, 13, used_life, format2)
                    #sheet.write(row, 14, remaining_life, format2)
                    sheet.write(row, 15, deliver, format2)
                    sheet.write(row, 16, return_deadline, format2)
                    sheet.write(row, 17, product_qty, format2)
                    #sheet.write(row, 18, product_cost, format2)
                    #sheet.write(row, 19, amount, format2)
                    #sheet.write(row, 20, back_charged, format2)
                    #sheet.write(row, 21, total, format2)
                    #sheet.write(row, 22, returned, format2)
                    #sheet.write(row, 23, remark, format2)

                    row = row + 1
                    
        except:
            
            for id in order_ids:
                if id.name:
                    mrf_number = id.name
                else:
                    mrf_number = None

                if id.transfer_order_type_id:
                    type = id.transfer_order_type_id.name
                else:
                    type = None

                if id.user_id:
                    requestor = id.user_id.name
                else:
                    requestor = None
                if id.delivery_deadline:
                   submission_date = id.delivery_deadline.strftime("%d/%m/%Y")
                else:
                    submission_date = None

                if id.date_request:
                   pick_up_date = id.date_request.strftime("%d/%m/%Y")
                else:
                    pick_up_date = None

                if id.date_order:
                    create_date = id.date_order.strftime("%d/%m/%Y")
                else:
                    create_date = None

                if id.date_delivered:
                    deliver = id.date_delivered.strftime("%d/%m/%Y")
                else:
                    deliver = None

                if id.return_deadline:
                    return_deadline = id.return_deadline.strftime("%d/%m/%Y")
                else:
                    return_deadline = None

                supplier = None
                site = None
                product_code = None
                product_qty = None
                if id.stock_transfer_order_line:
                    for line in id.stock_transfer_order_line:
                        if line.supplier_id:
                            supplier = line.supplier_id.name
                        else:
                            supplier = None

                        if line.project_id:
                            site = line.project_id.name
                        else:
                            site = None

                        if line.product_id.default_code:
                            product_code = product.product_id.default_code
                        else:
                            product_code = None

                        if line.delivered_qty:
                            product_qty = line.delivered_qty
                        else:
                            product_qty = None


                        sheet.write(row, 0, mrf_number, format2)
                        sheet.write(row, 1, type, format2)
                        sheet.write(row, 2, requestor, format2)
                        sheet.write(row, 3, supplier, format2)
                        sheet.write(row, 4, submission_date, format2)
                        sheet.write(row, 5, pick_up_date, format2)
                        #sheet.write(row, 6, penalty_effective_date, format2)
                        sheet.write(row, 7, create_date, format2)
                        sheet.write(row, 8, site, format2)
                        #sheet.write(row, 9, on_air, format2)
                        #sheet.write(row, 10, asset, format2)
                        sheet.write(row, 11, product_code, format2)
                        #sheet.write(row, 12, life_time, format2)
                        #sheet.write(row, 13, used_life, format2)
                        #sheet.write(row, 14, remaining_life, format2)
                        sheet.write(row, 15, deliver, format2)
                        sheet.write(row, 16, return_deadline, format2)
                        sheet.write(row, 17, product_qty, format2)
                        #sheet.write(row, 18, product_cost, format2)
                        #sheet.write(row, 19, amount, format2)
                        #sheet.write(row, 20, back_charged, format2)
                        #sheet.write(row, 21, total, format2)
                        #sheet.write(row, 22, returned, format2)
                        #sheet.write(row, 23, remark, format2)

                        row = row + 1
                else:
                    sheet.write(row, 0, mrf_number, format2)
                    sheet.write(row, 1, type, format2)
                    sheet.write(row, 2, requestor, format2)
                    sheet.write(row, 3, supplier, format2)
                    sheet.write(row, 4, submission_date, format2)
                    sheet.write(row, 5, pick_up_date, format2)
                    #sheet.write(row, 6, penalty_effective_date, format2)
                    sheet.write(row, 7, create_date, format2)
                    sheet.write(row, 8, site, format2)
                    #sheet.write(row, 9, on_air, format2)
                    #sheet.write(row, 10, asset, format2)
                    sheet.write(row, 11, product_code, format2)
                    #sheet.write(row, 12, life_time, format2)
                    #sheet.write(row, 13, used_life, format2)
                    #sheet.write(row, 14, remaining_life, format2)
                    sheet.write(row, 15, deliver, format2)
                    sheet.write(row, 16, return_deadline, format2)
                    sheet.write(row, 17, product_qty, format2)
                    #sheet.write(row, 18, product_cost, format2)
                    #sheet.write(row, 19, amount, format2)
                    #sheet.write(row, 20, back_charged, format2)
                    #sheet.write(row, 21, total, format2)
                    #sheet.write(row, 22, returned, format2)
                    #sheet.write(row, 23, remark, format2)

                    row = row + 1
                