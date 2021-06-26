from odoo import models


class GenerateXLSXReport(models.Model):
    _name = 'report.de_pr_line_report.pr_line_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Products Report')
        sheet.write(3, 0, 'PR No.', format1)
        sheet.write(3, 1, 'PR Date', format1)
        sheet.write(3, 2, 'PR Status', format1)
        sheet.write(3, 3, 'PR Line ID', format1)
        sheet.write(3, 4, 'Product', format1)
        sheet.write(3, 5, 'Product Category', format1)
        sheet.write(3, 6, 'Description', format1)
        sheet.write(3, 7, 'Cost Center', format1)
        sheet.write(3, 8, 'Site ID', format1)
        sheet.write(3, 9, 'Tenant', format1)
        sheet.write(3, 10, 'PR Line-quantity', format1)
        sheet.write(3, 11, 'UoM', format1)
        sheet.write(3, 12, 'Delivery Date', format1)
        sheet.write(3, 13, 'Unit Price', format1)
        sheet.write(3, 14, 'Subtoal Line Amount', format1)
        sheet.write(3, 15, 'Currency', format1)
        sheet.write(3, 16, 'PR Created by', format1)

        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter'})
        row = 4
        sheet.set_column(row, 0, 50)
        sheet.set_column(row, 1, 25)
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

        purchase_ids = self.env['purchase.requisition'].browse(data['id'])
        
        for id in purchase_ids:
            date = id.ordering_date
            if date:
                ordering_date = date.strftime("%m/%d/%Y")
            else:
                ordering_date = None
            sched_date = id.schedule_date
            if sched_date:
                delivery_date = sched_date.strftime("%m/%d/%Y")
            else:
                delivery_date = None
            for line in id.line_ids:
                category = line.product_id.categ_id.name

                sheet.write(row, 0, id.name, format2)
                sheet.write(row, 1, ordering_date, format2)
                sheet.write(row, 2, id.state, format2)
                sheet.write(row, 3, line.id, format2)
                sheet.write(row, 4, id.product_id.name, format2)
                sheet.write(row, 5, line.product_id.categ_id.name, format2)
                sheet.write(row, 6, line.product_description_variants, format2)
                sheet.write(row, 7, line.analytic_tag_ids.name, format2)
                sheet.write(row, 8, line.project_id.name, format2)
#                 sheet.write(row, 9, id.partner_id.name, format2)
                sheet.write(row, 10, line.product_qty, format2)
                sheet.write(row, 11, line.product_uom_id.name, format2)
                sheet.write(row, 12, delivery_date, format2)
                sheet.write(row, 13, line.price_unit, format2)
                sheet.write(row, 14, line.price_unit, format2)
                sheet.write(row, 15, id.currency_id.name, format2)
                sheet.write(row, 16, id.user_id.name, format2)

                row = row + 1
