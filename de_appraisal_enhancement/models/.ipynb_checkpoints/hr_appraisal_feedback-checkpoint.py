from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrAppraisalFeedback(models.Model):
    _name = 'hr.appraisal.feedback'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
#     objective_id = fields.Many2one('hr.appraisal.objective')
#     appraisal_id = fields.Many2one('hr.appraisal')

    company_id = fields.Many2one('res.company', default=lambda self:self.env.company.id)
    description = fields.Char('Description')
    
    
    name = fields.Many2one('hr.employee',string = 'Name')
    job_title = fields.Char('Job Title', related = 'name.job_title')
    manager = fields.Char('Manager', related = 'name.parent_id.name')
    department = fields.Char('Department', related = 'name.department_id.name')
#     date_joining = fields.Date('Date of Joining' related = 'name.contract_id.job_id.name')
    date_joining = fields.Date('Date of Joining')
#     grade = fields.Char('Grade', related = 'name.department_id.name')
    grade = fields.Char('Grade')
#      performance_period = fields.Float('Performance Period'related = 'name.department_id.name')
    performance_period = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                   , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                   , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                   , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                   , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                               string="Performance Period", readonly=True)
    note = fields.Text('Note', compute = 'get_default_note')
    
    objective_comment = fields.Text('Half Year Comments')
    full_year_objective_comment = fields.Text('Full Year Comments')
    value_comment = fields.Text('Half Year Comments')
    full_year_value_comment = fields.Text('Full Year Comments')
    
    half_year_appraiser_objective_comment = fields.Text('Half Year Comments')
    full_year_appraiser_objective_comment = fields.Text('Full Year Comments')
    half_year_appraiser_value_comment = fields.Text('Half Year Comments')
    full_year_appraiser_value_comment = fields.Text('Full Year Comments')
    
    employee_feedback = fields.Char('Employee Feedback')
    
    
    def unlink(self):
    	for rec in self:
    		if rec.state not in ['draft']:
    			raise UserError(('Deletion is Not Allowed!'))
    		return super(HrAppraisalFeedback, self).unlink()
    
    
    @api.onchange('name')
    def get_default_note(self):
        self.note =  """                        5 = Outstanding      Ratings: 451-500
                        Consistently and significantly exceeds all performance expectations
                        and standards. Demonstrates a personal commitment to a high level
                        of performance and results, even under challenging work goals. 
                        
                        4 = Exceed Expectations  Ratings: 376- 450
                        Frequently exceeds job requirements. Makes contributions well
                        beyond job demands. Commendable performance.
                        
                        3 = Met Expectations Ratings:  276 – 375
                        person in this position. All objectives and standards are met. Has good
                        job knowledge and is able to perform with minimum supervision.
                        
                        2 = Partially Met Expectations Ratings: 200 – 275
                        totally achieved. Person is capable of improving to an acceptable
                        standard.
                        
                        1 = Unacceptable performance  Ratings: Below 200
                        An individual who has performed inadequately in the objectives set for
                        her/his position.
       """
        
    mid_year_date = fields.Date('Mid Year Review Date')
    end_year_date = fields.Date('End Year Review Date')
    date_end_deadline = fields.Date('End Year Deadline Date')
    date_mid_deadline = fields.Date('Mid Year Deadline Date')
    
    objective_score = fields.Float('Business Objectives Accumulative Score', compute='compute_objective_score')
    objective_rating = fields.Char('Business Objectives Accumulative Rating')
    
    behavioral_score = fields.Float('Behavioral Accumulative Score', compute='compute_core_score')
    behavioral_rating = fields.Char('Behavioral Accumulative Rating')
    
    agreement = fields.Selection([
        ('not_agree', 'Not Agree'),
        ('partially', 'Partially Agree'),
        ('fully', 'Fully Agree'),
    ], string='Agreement With Half Year Evaluation', index=True, copy=False, default='partially', required = True, track_visibility='onchange')
    
    full_year_agreement = fields.Selection([
        ('not_agree', 'Not Agree'),
        ('partially', 'Partially Agree'),
        ('fully', 'Fully Agree'),
    ], string='Agreement With Full Year Evaluation', index=True, copy=False, default='partially', required = True, track_visibility='onchange')
    
    reason_for_disagreement = fields.Char('Reason For Disagreement')
    full_reason_for_disagreement = fields.Char('Full Year Reason For Disagreement')
    
    concerned_person = fields.Selection([
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ], string='Concerned Person', index=True, copy=False, default='employee', required = True, track_visibility='onchange')
    
    
    appraisal_period = fields.Selection([
        ('half_year', 'Half Year'),
        ('full_year', 'Full Year'),

    ], string='Appraisal Period', index=True, copy=False, default='half_year', required = True, track_visibility='onchange')
            
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange', tracking=True)
    
    feedback_objective_lines = fields.One2many('hr.appraisal.feedback.objective.line', 'feedback_id', tracking=True, track_visibility='onchange')
    feedback_values_lines = fields.One2many('hr.appraisal.feedback.values.line', 'feedback_id', tracking=True, track_visibility='onchange')
    feedback_promotion_lines = fields.One2many('hr.appraisal.feedback.promotion.line', 'feedback_id')
    feedback_training_lines = fields.One2many('hr.appraisal.feedback.training.line', 'feedback_id')
    feedback_objective_appraisee_lines = fields.One2many('hr.appraisal.feedback.objective.appraisee.line', 'feedback_id')
    feedback_values_appraisee_lines = fields.One2many('hr.appraisal.feedback.values.appraisee.line', 'feedback_id')
    
    
    strength_1 = fields.Char('Strengths/Achievements')
    strength_2 = fields.Char('strength')
    strength_3= fields.Char('strength')
    strength_4 = fields.Char('strength')
    strength_5= fields.Char('strength')

    improvements_1 = fields.Char('Weaknesses/Areas for Improvement')
    improvements_2 = fields.Char('improvements')
    improvements_3 = fields.Char('improvements')
    improvements_4 = fields.Char('improvements')
    improvements_5 = fields.Char('improvements')
    
    reason_1 = fields.Char('reason')
    reason_2 = fields.Char('reason')
    reason_3 = fields.Char('reason')
    reason_4 = fields.Char('reason')
    reason_5 = fields.Char('reason')
    
    training_1 = fields.Char('Training')
    training_2 = fields.Char('Training')
    training_3 = fields.Char('Training')
    training_4 = fields.Char('Training')
    training_5= fields.Char('Training')

    
    recommend_promotion = fields.Selection([('yes', 'Yes'),('no', 'No'),
    ], string='Recommended for Promotion?', index=True, copy=False, default='no',  required=True, track_visibility='onchange')
    promotion_position = fields.Char('Promotion To Position')
    promotion_grade = fields.Char('Promotion To Grade')
    date_effective = fields.Date('With Effect From')
    
    
    @api.onchange('feedback_objective_lines')
    def track_history(self):
        self.message_notify(body=_('Changes Recording'))
    
    @api.onchange('feedback_values_lines')
    def track_history(self):
        self.message_notify(body=_('Dear %s, Changes Recorded') % (self.env.user.name,), partner_ids=[self.env.user.partner_id.id])

    
    def compute_objective_score(self):
        sum = 0
        if self.feedback_objective_lines:
            for rec in self.feedback_objective_lines:
                sum = sum + rec.weightage_score
        self.objective_score = sum
        if round(self.objective_score,0) in range(451,501):
            self.objective_rating = 'Outstanding'
            
        elif round(self.objective_score,0) in range(376,451):
            self.objective_rating = 'Exceed Expectations'
        
        elif round(self.objective_score,0) in range(276,376):
            self.objective_rating = 'Met Expectations'
        elif round(self.objective_score,0) in range(200,276):
            self.objective_rating = 'Partially Met Expectations'
        elif round(self.objective_score,0) in range(1,200):
            self.objective_rating = 'Unacceptable'
        else:
            self.objective_rating = ' '
            
    
    def compute_core_score(self):
        sum = 0
        if self.feedback_values_lines:
            for rec in self.feedback_values_lines:
                sum = sum + rec.weightage_score
        self.behavioral_score = sum
        
        if round(self.behavioral_score,0) in range(451,501):
            self.behavioral_rating = 'Outstanding'
        elif round(self.behavioral_score,0) in range(376,451):
            self.behavioral_rating = 'Exceed Expectations'
        elif round(self.behavioral_score,0) in range(276,376):
            self.behavioral_rating = 'Met Expectations'
        elif round(self.behavioral_score,0) in range(200,276):
            self.behavioral_rating = 'Partially Met Expectations'
        elif round(self.behavioral_score,0) in range(1,200):
            self.behavioral_rating = 'Unacceptable'
        else:
            self.behavioral_rating = ' '
        
    def action_confirm(self):
        self.state = 'confirm'
        
    def employee_done(self):
        self.state = 'done'
    
#     def action_expired(self):
#         self.state = 'expired'
        
    def action_Sent_for_Employee_Review(self):
        self.state = 'sent'
        
    def action_endorsed_employee(self):
        self.state = 'endorsed_employee'
        
    def action_endorsed_hod(self):
        self.state = 'endorsed_hod'
        
    def action_done(self):
        self.state = 'done'
#         States After Done Controlled Here

    def action_end_year_appraisee_review(self):
        self.state = 'end_year_appraisee_review'
        
    def action_end_year_appraiser_review(self):
        self.state = 'end_year_appraiser_review'
    
    def action_end_year_sent_emp_view(self):
        self.state = 'end_year_sent_emp_view'
        
    def action_end_year_endorsed_emp(self):
        self.state = 'end_year_endorsed_emp'
        
    def action_end_year_endorse_hod(self):
        self.state = 'end_year_endorse_hod'
        
    def action_closed(self):
        self.state = 'closed'
        
    

class HrAppraisalFeedbackObjectiveLine(models.Model):
    _name = 'hr.appraisal.feedback.objective.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Remarks')
    full_remarks = fields.Char('Remarks')
    objective = fields.Char('Objective')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low', required = True, track_visibility='onchange')
    rating = fields.Integer('Full Year Rating', track_visibility='onchange')
    weightage_score = fields.Float('Weightage Score', compute='compute_weightage_score')
    percentage_score = fields.Selection([
        ('0', '0%'),
        ('1', '20%'),
        ('2', '40%'),
        ('3', '60%'),
        ('4', '80%'),
        ('5', '100%'),
    ], string='Half Year % Score', index=True, copy=False, default='0',required = True, track_visibility='onchange')
    comments = fields.Char('Comments')
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score = rec.weightage * (rec.rating / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    


class HrAppraisalFeedbackValuesLine(models.Model):
    _name = 'hr.appraisal.feedback.values.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Remarks')
    full_remarks = fields.Char('Remarks')
    core_values = fields.Char('Core Values')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low', required = True,track_visibility='onchange')
    rating = fields.Integer('Full Year Rating', track_visibility=True)
    weightage_score = fields.Float('Weightage Score', compute='compute_weightage_score')
    comments = fields.Char('Comments')
    conformance_level = fields.Selection([
        ('below', 'Below Average'),
        ('satisfactory', 'Satisfactory'),
        ('good', 'Good'),
        ('role_model', 'Role Model'),
    ], string='Half Year Conformance Level', index=True, copy=False, default='satisfactory', required = True, track_visibility=True)
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score = rec.weightage * (rec.rating / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    
class HrAppraisalFeedbackPromotionLine(models.Model):
    _name = 'hr.appraisal.feedback.promotion.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    
    recommend_promotion = fields.Selection([('yes', 'Yes'),('no', 'No'),
    ], string='Recommended for Promotion?', index=True, copy=False, default='no',  required=True, track_visibility='onchange')
    promotion_position = fields.Char('Promotion To Position')
    promotion_grade = fields.Char('Promotion To Grade')
    date_effective = fields.Date('With Effect From')
    
    
class HrAppraisalFeedbackTrainingLine(models.Model):
    _name = 'hr.appraisal.feedback.training.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    
    strength = fields.Char('Strengths/Achievements')
    improvements = fields.Char('Weaknesses/Areas for Improvement')
    training = fields.Char('Training Recommend')
    reason = fields.Char('Reason')

    
    
    
    
class HrAppraisalFeedbackObjectiveAppraiseeLine(models.Model):
    _name = 'hr.appraisal.feedback.objective.appraisee.line'

    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Remarks')
    full_remarks = fields.Char('Remarks')
    objective = fields.Char('Objective')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority',default='low')
    rating = fields.Integer('Full Year Rating')
    weightage_score = fields.Float('Weightage Score', compute='compute_weightage_score')
    percentage_score = fields.Selection([
        ('0', '0%'),
        ('1', '20%'),
        ('2', '40%'),
        ('3', '60%'),
        ('4', '80%'),
        ('5', '100%'),
    ], string='Half Year % Score', default='0')
    comments = fields.Char('Comments')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score = rec.weightage * (rec.rating / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')
    
    
class HrAppraisalFeedbackValuesAppraiseeLine(models.Model):
    _name = 'hr.appraisal.feedback.values.appraisee.line'
    
    feedback_id = fields.Many2one('hr.appraisal.feedback')
    appraisal_period = fields.Selection(related='feedback_id.appraisal_period')
    concerned_person = fields.Selection(related='feedback_id.concerned_person')
    remarks = fields.Char('Remarks')
    full_remarks = fields.Char('Remarks')
    core_values = fields.Char('Core Values')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', default='low')
    rating = fields.Integer('Full Year Rating')
    weightage_score = fields.Float('Weightage Score', compute='compute_weightage_score')
    comments = fields.Char('Comments')
    conformance_level = fields.Selection([
        ('below', 'Below Average'),
        ('satisfactory', 'Satisfactory'),
        ('good', 'Good'),
        ('role_model', 'Role Model'),
    ], string='Half Year Conformance Level', default='satisfactory')
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('expired', 'Expired'),
        ('sent', 'Sent for Employee Review'),
        ('endorsed_employee', 'Endorsed by Employee'),
        ('endorsed_hod', 'Endorsed by HOD'),
        ('done', 'Done'),
        ('end_year_appraisee_review', 'End Year Appraisee Review'),
        ('end_year_appraiser_review', 'End Year Appraiser Review'),
        ('end_year_sent_emp_view', 'End Year Sent for Emp Review'),
        ('end_year_endorsed_emp', 'End Year Endorsed by Emp'),
        ('end_year_endorse_hod', 'End Year Endorsed by HOD'),
        ('closed', 'Closed'),
        
    ], string='State', related='feedback_id.state')
    
    def compute_weightage_score(self):
        for rec in self:
            rec.weightage_score = rec.weightage * (rec.rating / 100)
    
    @api.onchange('rating')
    def limit_rating(self):
        if self.rating:
            for rec in self:
                if rec.rating > 500 or rec.rating <= 0:
                    raise UserError('Rating Cannot be greater than 500 or less than 1')