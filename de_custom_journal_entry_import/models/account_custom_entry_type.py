
from odoo import api, fields, models, tools, _



class IrAttachment(models.Model):
    
    _inherit = 'account.custom.entry.type'
    
    
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_custom_entry_type",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment")
    is_publish = fields.Bolean(string='Publish on Website')
    


