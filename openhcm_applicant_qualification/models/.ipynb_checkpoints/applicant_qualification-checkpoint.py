from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    # foreign key concept
    qualification_lines = fields.One2many('hr.applicant.qualification', 'qualification_tab',)

    avg_score = fields.Float(compute='compute_score_average',store=True,index=True, string='Average Score')

    @api.depends('qualification_lines.score')
    def compute_score_average(self):

        for applicant in self:
            computed_avg = 0
            count = 0
            summation = 0
            # for line in self.qualification_lines:
            for line in applicant.qualification_lines:
                count = count + 1
                summation = line.score + summation
            if count > 0:
                computed_avg = summation / count
            else:
                computed_avg = 0

            applicant.avg_score = computed_avg
            # applicant.update({
            #     'avg_score': computed_avg
            # })
        # self.env.cr.commit()

    # @api.model
    # def create(self, vals):
    #     # get_job = vals.get('job_id.name')
    #     get_avg = vals.set('avg_score')
    #     print("1=======================",vals.get('avg_score'))
    #     # print("2=======================",vals['avg_score'])
    #     print("3=======================",self.avg_score)
    #
    #     job_position = self.env['hr.job'].search([('id', '=', vals['job_id'] )])
    #     for job in job_position:
    #         print('=================================', job.qualifying_score)
    #         if job.qualifying_score <= vals['avg_score']:
    #             if job.next_stage_id:
    #                 vals.update({
    #                     'stage_id': job.next_stage_id,
    #                 })
    #
    #     res = super(HrApplicant, self).create(vals)
    #     return res



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

    qualification_tab = fields.Many2one('hr.applicant', string='Qualification')

    qualification_type_id = fields.Many2one('hr.applicant.qualification.rule', string='Qualification Type', required=True)
    qualification_type_line_id = fields.Many2one(related='qualification_type_id.qualification_type_line_id')
    score = fields.Float(related='qualification_type_line_id.score')


    def cal_score(self):
        for record in self:
            record.score = record.qualification_type_line_id.score

    @api.onchange('qualification_type_line_id')
    def onchange_score(self):
        for record in self:
            record.score = self.qualification_type_line_id.score
