
from odoo import api, fields, models, tools, _

IMPORT_SELECTION = [
    ('required', 'Required'),
    ('no', 'None')]

class IrAttachment(models.Model):
    
    _inherit = 'account.custom.entry.type'
    
    
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_custom_entry_type",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Create Attachment")
    update_attachment_id = fields.Many2many('ir.attachment', relation="files_rel_custom_entry_type_update",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Update Attachment")
    is_publish = fields.Boolean(string='Publish on Website')
    has_create_attaachment = fields.Boolean(string="Reference Attachment On Creation")
    has_edit_attachment = fields.Boolean(string="Reference Attachment On Updation")


