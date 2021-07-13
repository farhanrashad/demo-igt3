from odoo import api, fields, models, _
from . import applicant_qualification_type


class HrEmployee(models.Model):
    _inherit = 'hr.job'
    # foreign key concept
    document_lines = fields.One2many('hr.applicant.qualification.rule', 'recruitment_tab')

    qualifying_score = fields.Integer(string='Qualifying Score')
    is_stage_change = fields.Boolean(string='State')
    next_stage_id = fields.Many2one('hr.recruitment.stage',)



class QualificationRule(models.Model):

    _name = 'hr.applicant.qualification.rule'
    _description = 'Applicant Qualification Rule'

    recruitment_tab = fields.Many2one('hr.job', string='Recruitment')

    name = fields.Many2one('hr.applicant.qualification.type', string='Type', required=True)
    qualification_type_line_id = fields.Many2one('hr.applicant.qualification.type.line', string='Line Type', required=True)
    score = fields.Float(string='Score',compute='cal_score', readonly=1)

    qualifying_score = fields.Integer(string='Qualifying Score')
    is_stage_change = fields.Boolean(string='State')
    next_stage_id = fields.Many2one('hr.recruitment.stage',)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(name=False, qualification_type_line_id=False, score=0.0, qualifying_score=0, is_stage_change=False, next_stage_id=False)

        cr = super(QualificationRule, self).create(vals_list)
        return cr

    @api.depends('score')
    def total(self):
        self.total_score = 0
        for record in self:
            record.total_score = int(record.qualification_type_line_id.score) + record.total_score
            print(record.qualification_type_line_id.score)

    def cal_score(self):
        for record in self:
            record.score = record.qualification_type_line_id.score


    @api.onchange('qualification_type_line_id')
    def onchange_score(self):
        for record in self:
            record.score = self.qualification_type_line_id.score
