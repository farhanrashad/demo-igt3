# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_hr_overtime(models.Model):
#     _name = 'de_hr_overtime.de_hr_overtime'
#     _description = 'de_hr_overtime.de_hr_overtime'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
