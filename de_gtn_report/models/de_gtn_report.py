from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date


class GtnReportPrint(models.Model):
    _inherit = 'stock.picking'

    # table 1 left side
    gtn_number = fields.Char(string="GTN Number")
    Project_name = fields.Char(string='Project Name')
    mrf_ref_no = fields.Char(string='Mrf Ref No')
    tower_type = fields.Selection([('tubular', 'Tubular'), ('angular', 'Angular')], string='Tower Type')
    site_address = fields.Char(string=' Site Address')
    contractor_name = fields.Many2one('res.partner', string='Contractor Name')
    contractor_description = fields.Char(string='Description')

    # table 1 right side

    date_of_gtn = fields.Char(string=' Date of GTN')
    igt_site_id = fields.Char(string=' IGT Site Id')
    telenor_site_id = fields.Char(string='Telenor Site Id')
    tower_height = fields.Float(string='Tower Height')
    transporter_name = fields.Many2one('res.partner', string='Transporter Name ')
    contact_no = fields.Char(string='Contact No')

    # tabel 2 left
    serial = fields.Char(string='Serial #')
    product_code = fields.Char(string='Product Code')
    description = fields.Char(string='Description')
    # tabel 2 right
    material_supplier_name = fields.Char(string='Material Supplier Name')
    mrf_qty = fields.Char(string='MRF Qty')
    quantity = fields.Char(string='Quantity')

    # tale 3 left side
    for_irrawady_green_tower_ltd = fields.Char(string='For Irrawady Green Tower Ltd')
    # representative_name = fields.Char(string='For Irrawady Green Tower Ltd')
    name_of_authorized_person = fields.Char(string='Name Of Authorized Person')
    designation = fields.Char(string='Designation')
    authorized_signature_date = fields.Char(string='Authorized Signature / Date')
    contact = fields.Char(string='Contact No')
    gate_pass_form_no = fields.Char(string='Gate Pass Form No')

    # table 3 right side
    for_contractors = fields.Char(string='For Contractors')
    name_of_authorized = fields.Char(string='Name Of Authorized Person')
    contact_number = fields.Char(string='Contact Number')
    drive_name = fields.Char(string='Drive Name')
    contact_contractors = fields.Char(string='Contact Contractors')
    vehicle_no = fields.Char(string='Vehicle No')

    # table 4
    any_damage = fields.Char(string='Any Damage')
    registered_office_address = fields.Char(string='Registered Office Address')
