# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

    
class EmployeeTrainingSessions(models.Model):
    _name = 'hr.employee.training.session'
    _description = 'HR Employee Training Sessions'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name desc'
    
    def action_session_send(self):
        template_id = self.env.ref('openhcm_employee_training.email_template_edi_sessions_case').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        self.write({
            'state': 'scheduled',
        })    
        
    def action_process(self):
        self.write({
            'state': 'approval',
        })    
       
    def action_close(self):
        self.write({
            'state': 'cancelled',
        })
        
    def action_completed(self):
        self.write({
            'state': 'completed',
        })    
        

    name = fields.Char(string='Order Reference',  copy=False,  index=True,readonly=True,default=lambda self: _('New'))
    delivery_method = fields.Many2one('hr.employee.training.course.delivery.method', string='Delivery Method', store=True, states={'draft': [('readonly', False)]},)
    start_date = fields.Date(string='Start Date', store=True, required=True)
    end_date = fields.Date(string='End Date', store=True, required=True)
    delivery_location = fields.Char(string='Delivery Location', store=True)
    note = fields.Html(string="Description" )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approval', 'Approval'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    trainer_lines = fields.One2many('hr.employee.training.session.trainers', 'session_id', string='Trainer Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True, auto_join=True)
    participants_lines = fields.One2many('hr.employee.training.session.participants', 'session_id', string='Trainer Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True, auto_join=True)

    
        
    @api.model
    def create(self,values):
        seq = self.env['ir.sequence'].get('hr.employee.training.session') 
        values['name'] = seq
        res = super(EmployeeTrainingSessions,self).create(values)
        return res
    
    
    
class TrainingCourseTrainers(models.Model):
    _name = 'hr.employee.training.session.trainers'
    _description = 'HR Employee Training Sessions Trainers'


    session_id = fields.Many2one('hr.employee.training.session',string='Sessions', store=True)
    trainer_id = fields.Many2one('res.partner',string='Trainer', store=True)
   
    
    
class TrainingCourseParticipants(models.Model):
    _name = 'hr.employee.training.session.participants'
    _description = 'HR Employee Training Course Participants'


    session_id = fields.Many2one('hr.employee.training.session',string='Sessions', store=True)
    employee_id = fields.Many2one('res.partner',string='Participants', store=True)  