from odoo import api, fields, models, _


class HrApplicantInherit(models.Model):
    _inherit = 'hr.applicant'

    qualification_lines = fields.One2many('hr.applicant.qualification', 'qualification_id',)
    avg_score = fields.Float(compute='compute_score_average',store=True,index=True, string='Average Score')

    @api.depends('qualification_lines.score')
    def compute_score_average(self):
        for applicant in self:
            computed_avg = 0
            count = 0
            summation = 0
            for line in applicant.qualification_lines:
                if line.score:
                    count = count + 1
                    summation = line.score + summation
                if count > 0:
                    computed_avg = summation / count
                else:
                    computed_avg = 0
            else:
                pass

            applicant.avg_score = computed_avg


    @api.onchange('job_id')
    def onchange_job(self):
        data = []
        for other_input in self.qualification_lines:
            other_input.unlink()

        if self.job_id:
            for record in self.job_id.document_lines:
                data.append((0, 0, {
                    'qualification_type_id': record.id,
                    'qualification_type_line_id': record.qualification_type_line_id,
                    'score': record.score,
                }))
            self.qualification_lines = data

class Qualification(models.Model):
    _name = 'hr.applicant.qualification'
    _description = 'Applicant Qualification'

    name = fields.Char(string='Section')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    qualification_id = fields.Many2one('hr.applicant', string='Qualification')
    qualification_type_id = fields.Many2one('hr.applicant.qualification.rule', string='Qualification Type')
    qualification_type_line_id = fields.Many2one(related='qualification_type_id.qualification_type_line_id')
    score = fields.Float(related='qualification_type_line_id.score')


    def cal_score(self):
        for record in self:
            record.score = record.qualification_type_line_id.score

    @api.onchange('qualification_type_line_id')
    def onchange_score(self):
        for record in self:
            record.score = self.qualification_type_line_id.score
