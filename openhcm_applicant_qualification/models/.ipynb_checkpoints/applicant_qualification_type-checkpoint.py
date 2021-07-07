from odoo import api, fields, models, _


class QualificationType(models.Model):
    _name = 'hr.applicant.qualification.type'
    _description = 'Applicant Qualification Type'

    name = fields.Char(string='Name', required=True)
    qualification_type_line = fields.One2many('hr.applicant.qualification.type.line', 'qualification_type_id')


class LineItem(models.Model):
    _name = 'hr.applicant.qualification.type.line'
    _description = 'Applicant Qualification Type Line'

    qualification_type_id = fields.Many2one('hr.applicant.qualification.type', string='Qualification Type')

    name = fields.Char(string='Value',required=True)
    score = fields.Float(string='Score', required=True)
