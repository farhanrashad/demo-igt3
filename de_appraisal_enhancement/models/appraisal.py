from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
from datetime import date, datetime, timedelta

class HrAppraisalInherit(models.Model):
    _inherit = 'hr.appraisal'
    
    appraisal_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')
                                   , ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027')
                                   , ('2028', '2028'), ('2029', '2029'), ('2030', '2031'), ('2032', '2032')
                                   , ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
                                   , ('2037', '2037'), ('2038', '2038'), ('2039', '2039'), ('2040', '2040')],
                               string="Appraisal Year", required = "required")
    date_end = fields.Date('End year Review Date')
    date_mid = fields.Date('Mid year Review Date')
    description = fields.Char('Description')
    employee_objectives = fields.Char('Objectives')
    employee_feedback = fields.Char('Feedback')
    
    def action_done(self):
        self.state = 'done'
    
    def unlink(self):
    	for rec in self:
    		if rec.state in ['done']:
    			raise UserError(('Deletion is Not Allowed!'))
    		return super(HrAppraisalInherit, self).unlink()    
        
    
    @api.onchange('date_end')
    def check_end_date(self):
        if self.date_mid > self.date_end:
            raise UserError(('Mid Year Review Date Cannot Be Greater Than End Year Review Date'))

        
    @api.model
    def create(self,vals):
        if vals['appraisal_year']:
            appraisal_exists = self.search([('state', '!=', 'cancel'),('employee_id','=',vals['employee_id']),('appraisal_year','=',vals['appraisal_year'])])
            if appraisal_exists:
                raise UserError(('Appraisal Already Exist for Selected Year'))
        result = super(HrAppraisalInherit, self).create(vals)
        return result 
    

    def auto_appraisal_cron(self):
        for appraisal_record in self.search([('state', '=', 'pending')]):
                appraisal_record.create_appraisal_record_action()

    
    def create_appraisal_record_action(self):
        appraisals = []
        for appraisal in self.search([('state', '=', 'pending')]):
            appraisals.append(appraisal)
        self.create_appraisal_record(appraisals)
        
    def action_view_feedback_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('FeedBack'),
            'res_model': 'hr.appraisal.feedback',
            'view_mode': 'tree',
            'view_id': self.env.ref('de_appraisal_enhancement.view_hr_appraisal_feedback_tree', False).id,
            'domain': [('name', '=', self.employee_id.id),('performance_period', '=', self.appraisal_year)],
        }
    
    def action_view_objective_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Objective'),
            'res_model': 'hr.appraisal.objective',
            'view_mode': 'tree',
            'view_id': self.env.ref('de_appraisal_enhancement.view_hr_appraisal_objective_tree', False).id,
            'domain': [('employee_id', '=', self.employee_id.id),('objective_year', '=', self.appraisal_year)],
        }
        
    
    def create_appraisal_record(self, appraisals):
        for record in appraisals:
            mid_start_date = self.date_mid
            mid_deadline_date = mid_start_date + timedelta(days=10)
            end_start_date = self.date_end
            end_deadline_date = end_start_date + timedelta(days=10)
            rec =  self.env['hr.appraisal.feedback'].create({
                'name': record.employee_id.id,
                'performance_period': record.appraisal_year,
                'mid_year_date': record.date_mid,
                'date_mid_deadline': mid_deadline_date,
                'end_year_date': record.date_end,
                'date_end_deadline': end_deadline_date,
            })

            objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
            if objective_ids:
                if objective_ids.objective_lines:
                    for line in objective_ids.objective_lines:
                        self.env['hr.appraisal.feedback.objective.line'].create({
                            'objective': line.objective,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })


            value_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
            if value_ids:
                if value_ids.values_lines:
                    for line in value_ids.values_lines:
                        self.env['hr.appraisal.feedback.values.line'].create({
                            'core_values': line.core_value,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id})
                        
            objective_appraisee_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
            if objective_ids:
                if objective_ids.objective_lines:
                    for line in objective_ids.objective_lines:
                        self.env['hr.appraisal.feedback.objective.appraisee.line'].create({
                            'objective': line.objective,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })
                        
            value_appraisee_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
            if value_ids:
                if value_ids.values_lines:
                    for line in value_ids.values_lines:
                        self.env['hr.appraisal.feedback.values.appraisee.line'].create({
                            'core_values': line.core_value,
                            'weightage': line.weightage,
                            'priority': line.priority,
                            'feedback_id': rec.id
                        })
                        
                        
#         for record in appraisals: 
#             current_date = date.today()
#             end_date = current_date + timedelta(days=365)
            
#             if current_date == record.date_mid:
#                 emp_start_date = self.date_mid
#                 emp_deadline_date = emp_start_date + timedelta(days=5)
#                 mgr_start_date = emp_deadline_date + timedelta(days=1)
#                 mgr_deadline_date = mgr_start_date + timedelta(days=5)
#                 for i in range(2):
                    
#                     if i == 0:
#                         start_date = emp_start_date
#                         deadline_date = emp_deadline_date
#                         person = 'employee'
#                     else:
#                         start_date = mgr_start_date
#                         deadline_date = mgr_deadline_date
#                         person = 'manager'
#                     rec =  self.env['hr.appraisal.feedback'].create({
#                                 'name': record.employee_id.id,
#                                 'appraisal_period': 'half_year',
#                                 'concerned_person': person,
#                                 'performance_period': self.appraisal_year,
#                                 'date_start': start_date,
#                                 'date_deadline': deadline_date,
                        
#                                 })

#                     objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
#                     if objective_ids:
#                         for line in objective_ids.objective_lines:

#                             self.env['hr.appraisal.feedback.objective.line'].create({
#                                 'objective': line.objective,
#                                 'weightage': line.weightage,
#                                 'priority': line.priority,
#                                 'feedback_id': rec.id})


#                     value_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
#                     if value_ids:
#                         for line in value_ids.values_lines:
#                             self.env['hr.appraisal.feedback.values.line'].create({
#                                 'core_values': line.core_value,
#                                 'objective': line.description,
#                                 'weightage': line.weightage,
#                                 'priority': line.priority,
#                                 'feedback_id': rec.id})

                            

#             if current_date == record.date_end:
#                 emp_start_date = self.date_end
#                 emp_deadline_date = emp_start_date + timedelta(days=5)
#                 mgr_start_date = emp_deadline_date + timedelta(days=1)
#                 mgr_deadline_date = mgr_start_date + timedelta(days=5)
#                 for i in range(2):
#                     if i == 0:
#                         start_date = emp_start_date
#                         deadline_date = emp_deadline_date
#                         person = 'employee'
#                     else:
#                         start_date = mgr_start_date
#                         deadline_date = mgr_deadline_date
#                         person = 'manager'
#                     rec =  self.env['hr.appraisal.feedback'].create({
#                                             'name': record.employee_id.id,
#                                             'appraisal_period': 'full_year',
#                                             'concerned_person': person,
#                                             'performance_period': self.appraisal_year,
#                                             'date_start': start_date,
#                                             'date_deadline': deadline_date,
#                                             })

#                     objective_ids = self.env['hr.appraisal.objective'].search([('employee_id', '=',record.employee_id.id),('objective_year', '=',record.appraisal_year)])
#                     if objective_ids:
#                         for line in objective_ids.objective_lines:
#                             self.env['hr.appraisal.feedback.objective.line'].create({
#                                             'objective': line.objective,
#                                             'weightage': line.weightage,
#                                             'priority': line.priority,
#                                             'feedback_id': rec.id})


#                     value_ids = self.env['hr.appraisal.values'].search([('company_id','=',record.company_id.id)], order='company_id asc',limit=1)
#                     if value_ids:
#                         for line in value_ids.values_lines:
#                             self.env['hr.appraisal.feedback.values.line'].create({
#                                             'core_values': line.core_value,
#                                             'objective': line.description,
#                                             'weightage': line.weightage,
#                                             'priority': line.priority,
#                                             'feedback_id': rec.id})
