from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrAppraisalObjective(models.Model):
    _name = 'hr.appraisal.objective'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee')
    description = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Employee Review'),
        ('confirm', 'Confirmed'),
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')
    
    objective_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                   , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                   , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                   , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                   , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                               string="Objective Year", required = 'True')
    
    objective_lines = fields.One2many('hr.appraisal.objective.line', 'objective_id')
    
    total_weightage = fields.Float("Total Weightage", compute = 'limit_weightage')
    
    readonly_status = fields.Selection([
        ('make_readonly', 'Readonly'),
        ('make_editable', 'Editable')], compute = 'compute_readonly')
    
    def unlink(self):
        for rec in self:
            if rec.state in ['confirm']:
                raise UserError(('Deletion is Not Allowed!'))
            return super(HrAppraisalObjective, self).unlink()
    
     
    @api.onchange('employee_id')
    def compute_readonly(self):
        for rec in self:
            if rec.state == 'confirm' and rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_editable'
            if rec.state == 'confirm' and not rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_readonly'
            else:
                rec.readonly_status = 'make_editable'
    
    @api.onchange('objective_year')
    def onchange_objective_year(self):
        if self.objective_year:
            if self.employee_id.id:
                appraisal_exists = self.search([('employee_id','=',self.employee_id.id),('objective_year','=',self.objective_year)])
                if appraisal_exists:
                    raise UserError(('Objective Already exist for this year'))
            else:
                raise UserError(('First select the employee'))

    
    @api.model
    def create(self,vals):
        if vals['objective_year']:
            appraisal_exists = self.search([('state', '!=', 'cancel'),('employee_id','=',vals['employee_id']),('objective_year','=',vals['objective_year'])])
            if appraisal_exists:
                raise UserError(('Objective Already Exist for Selected Year'))
        result = super(HrAppraisalObjective, self).create(vals)
        return result


    
    @api.constrains('weightage')
    def limit_weightage(self):
        for rec in self:
            count = 0
            for line in rec.objective_lines:
                count = count + line.weightage
         
            rec.total_weightage = count

    @api.model
    def create(self,vals):
        res = super(HrAppraisalObjective, self).create(vals)
        if res.total_weightage != 100:
            raise UserError('Total Weightage must be equal 100')
        return res
    
    def write(self, vals):
        res = super(HrAppraisalObjective, self).write(vals)
        if self.total_weightage != 100:
            raise UserError('Total Weightage must be equal 100')
        return res
    
    
    def action_sent_review(self):
        self.state = 'waiting'
        
    def action_submit(self):
        self.state = 'confirm'    
        
    
class HrAppraisalObjectiveline(models.Model):
    _name = 'hr.appraisal.objective.line'
    
    objective_id = fields.Many2one('hr.appraisal.objective')
    objective = fields.Char('Objective')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low',required = True, track_visibility='onchange')
    
    @api.onchange('weightage')
    def limit_weightage(self):
        if self.weightage:
            for rec in self:
                if rec.weightage > 100 or rec.weightage <1:
                    raise UserError('Weightage Cannot be greater than 100 or less than 1')
                
    
    
    

    