from odoo import api, fields, models, _


class HrJobInherit(models.Model):
    _inherit = 'hr.job'

    document_lines = fields.One2many('hr.applicant.qualification.rule', 'recruitment_id')
    qualifying_score = fields.Integer(string='Qualifying Score')
    is_stage_change = fields.Boolean(string='State')
    next_stage_id = fields.Many2one('hr.recruitment.stage',)


class QualificationRule(models.Model):
    _name = 'hr.applicant.qualification.rule'
    _description = 'Applicant Qualification Rule'

    recruitment_id = fields.Many2one('hr.job', string='Recruitment')
    name = fields.Many2one('hr.applicant.qualification.type', string='Type')
    qualification_type_line_id = fields.Many2one('hr.applicant.qualification.type.line', string='Line Type', )
    score = fields.Float(string='Score',compute='score_calculation', readonly=1)

    @api.depends('score')
    def total(self):
        self.total_score = 0
        for record in self:
            record.total_score = int(record.qualification_type_line_id.score) + record.total_score
            print(record.qualification_type_line_id.score)

    def score_calculation(self):
        for record in self:
            record.score = record.qualification_type_line_id.score

    @api.onchange('qualification_type_line_id')
    def onchange_score(self):
        for record in self:
            record.score = self.qualification_type_line_id.score