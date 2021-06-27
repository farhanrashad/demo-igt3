from odoo import models


class GenerateXLSXReport(models.Model):
    _name = 'report.de_pos_sales_report.sale_analysis_report_xlsx'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        format1 = workbook.add_format({'font_size': '12', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Products Report')
        sheet.write(3, 0, 'BranchName', format1)
        sheet.write(3, 1, 'Cashier', format1)
        sheet.write(3, 2, 'InvoiceDate', format1)
        sheet.write(3, 3, 'ProductCategory', format1)
        sheet.write(3, 4, 'InvoiceNumber', format1)
        sheet.write(3, 5, 'InvoiceAmount', format1)
        sheet.write(3, 6, 'Discount', format1)
        sheet.write(3, 7, 'SubTotal', format1)
        sheet.write(3, 8, 'PaymentMethod', format1)
        sheet.write(3, 9, 'Customer', format1)
        sheet.write(3, 10, 'CustomerMobile', format1)
        sheet.write(3, 11, 'Barcode', format1)
        sheet.write(3, 12, 'InternalReference', format1)
        sheet.write(3, 13, '1-STYLE', format1)
        sheet.write(3, 14, 'FABRICDESIGN', format1)
        sheet.write(3, 15, '5-STYLE', format1)
        sheet.write(3, 16, 'FABRIC CODE', format1)
        sheet.write(3, 17, 'FABRIC COMPOSITION', format1)
        sheet.write(3, 18, 'FABRIC COLOR', format1)
        sheet.write(3, 19, 'SEASON', format1)
        sheet.write(3, 20, 'ORDER TYPE', format1)
        sheet.write(3, 21, 'Variant', format1)
        sheet.write(3, 22, 'Product Type', format1)

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
        sheet.set_column(row, 17, 20)
        sheet.set_column(row, 18, 20)
        sheet.set_column(row, 19, 20)
        sheet.set_column(row, 20, 20)
        sheet.set_column(row, 21, 20)
        sheet.set_column(row, 22, 20)

        config_ids = self.env['pos.order'].search([('id','in',data['config_ids'])])
        
        for line in config_ids.lines:
            
            for property in line.product_id.product_property_line:
                product_property = property.product_property_id.name
                
                if product_property == '1-STYLE':
                    one_style_short_value = property.product_property_line_id.name
                    
                elif product_property == 'FABRIC DESIGN':
                    fabric_design_short_value = property.product_property_line_id.name
                
                elif product_property == '5-STYLE':
                    five_style_short_value = property.product_property_line_id.name
                
                elif product_property == 'FABRIC CODE':
                    fabric_code_short_value = property.product_property_line_id.name

                elif product_property == 'FABRIC COMPOSITION':
                    fabric_comp_short_value = property.product_property_line_id.name
                
                elif product_property == 'FABRIC COLOR':
                    fabric_color_short_value = property.product_property_line_id.name
                
                elif product_property == 'SEASON':
                    season_short_value = property.product_property_line_id.name
                
                elif product_property == 'ORDER TYPE':
                    order_type_short_value = property.product_property_line_id.name


            parent_parent_category = line.product_id.categ_id.parent_id.parent_id.name
            parent_category = line.product_id.categ_id.parent_id.name
            category = parent_parent_category + '/' + parent_category + '/' + line.product_id.categ_id.name
            date = config_ids.date_order
            invoice_date = date.strftime("%m/%d/%Y, %H:%M:%S")
            
            values = []
            for val in line.product_id.attribute_line_ids.value_ids:
                values.append(val.name)
            value = ' '.join(values)
            
            sheet.write(row, 0, config_ids.name, format2)
            sheet.write(row, 1, config_ids.user_id.name, format2)
            sheet.write(row, 2, invoice_date, format2)
            sheet.write(row, 3, category, format2)
            sheet.write(row, 4, config_ids.pos_reference, format2)
            sheet.write(row, 5, config_ids.payment_ids.amount, format2)
            sheet.write(row, 6, line.discount, format2)
            sheet.write(row, 7, line.price_subtotal_incl, format2)
            sheet.write(row, 8, config_ids.payment_ids.payment_method_id.name, format2)
            sheet.write(row, 9, config_ids.partner_id.name, format2)
            sheet.write(row, 10, config_ids.partner_id.phone, format2)
            sheet.write(row, 11, line.product_id.barcode, format2)
            sheet.write(row, 12, line.product_id.default_code, format2)
            sheet.write(row, 13, one_style_short_value, format2)
            sheet.write(row, 14, fabric_design_short_value, format2)
            sheet.write(row, 15, five_style_short_value, format2)
            sheet.write(row, 16, fabric_code_short_value, format2)
            sheet.write(row, 17, fabric_comp_short_value, format2)
            sheet.write(row, 18, fabric_color_short_value, format2)
            sheet.write(row, 19, season_short_value, format2)
            sheet.write(row, 20, order_type_short_value, format2)
            sheet.write(row, 21, value, format2)
            sheet.write(row, 22, line.product_id.type, format2)

            row = row + 1
