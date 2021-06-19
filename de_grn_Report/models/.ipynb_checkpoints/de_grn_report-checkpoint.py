from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date


class GrnReportPrint(models.Model):
    _inherit = 'stock.picking'

    # table 1 left side
    gate_entry_no = fields.Char(string="Gate Entry No")
    gate_entry_date = fields.Char(string='Gate Entry Date')
    erp_grn_no = fields.Char(string='ERP GRN No')
    vendor_supplier_name = fields.Char(string='Vendor Supplier Name')
    purchase_order_no = fields.Char(string='Purchase Order No')
    vendor_invoice_no = fields.Char(string='Vendor Invoice No')
    vendor_picking_list = fields.Char(string='Vendor Picking No')
    material_related_to = fields.Char(string='Material Related To')
    tower_heigh = fields.Char(string='Tower Height')
    tower_wind_speed = fields.Char(string='Tower Wind Speed')
    type = fields.Char(string='Type')
    
    cha_name = fields.Char(string='CHA Name')
    container_no = fields.Char(string='Container No')
    no_of_container = fields.Char(string='Number of Container')

    truck_no = fields.Char(string='Truck No')
    mode_of_transport = fields.Char(string='Mode of Transport')
    no_of_trucks = fields.Char(string='Number of Trucks')
    
    sr_no = fields.Char(string='Sr.No')
    item_code = fields.Char(string='Item Code')
    grn_description = fields.Char(string='Description')
    
    quantity_ordered = fields.Char(string='Quantity Ordered')
    received_quantity = fields.Char(string='Received Quantity')
    receiver_Comments = fields.Char(string='Receiver Comments')

    name_1 = fields.Char(string='Name')
    name_2 = fields.Char(string='Name')
    position = fields.Char(string='Position')
    position_2 = fields.Char(string='Position')
    date_inspected = fields.Char(string='Date Received and Inspected ')
    date = fields.Char(string='Date')
    inspected_signature = fields.Char(string='Signature')
    signature_second = fields.Char(string='Signature')


    # table 1 right side
