from odoo import api, fields, models,_


class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    employee_family_ids = fields.One2many('hr.employee.family', 'employee_id')


class HrEmployeeFamily(models.Model):

    _name = 'hr.employee.family'
    _description = "Employee Family"



    name = fields.Char(string="Name",required=True)
    mobile = fields.Integer(string="Mobile")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    relation_ship = fields.Selection([('father','Father'),
                                      ('mother','Mother'),
                                      ('brother','Brother'),
                                      ('sister','Sister'),
                                      ('husband','Husband'),
                                      ('wife','Wife'),
                                      ('child','Child')], string='Relationship',required=True, default='father')

    date_of_birth = fields.Date()
    # visible_field = fields.Boolean(default=False)
    employee_id = fields.Many2one('hr.employee')


