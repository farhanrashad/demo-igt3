# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    
    sequence_code = fields.Char(string="Sequence Code")
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',
        copy=False, check_company=True)
    company_id = fields.Many2one(
        'res.company', 'Company', copy=False,
        required=True, index=True, default=lambda s: s.env.company)
    
    
    
    
    @api.model
    def create(self, vals):
        if vals.get('sequence_code'):
            sequence = self.env['ir.sequence'].create({
                'name': _('Sequence') + ' ' + vals['sequence_code'],
                'padding': 5,
                'prefix': vals['sequence_code'],
                'company_id': vals.get('company_id'),
            })
            vals['sequence_id'] = sequence.id

        categ = super().create(vals)
        return categ

    def write(self, vals):
        if 'sequence_code' in vals:
            for categ in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if categ.sequence_id:
                    categ.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', categ.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    categ.sequence_id = sequence
        if 'company_id' in vals:
            for categ in self:
                if categ.sequence_id:
                    categ.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)
    
    
    
    

