# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
import cx_Oracle
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)



class OracleSettingConnector(models.Model):
    _name = 'oracle.setting.connector'
    _description = 'Oracle Database Instance'
    _order = "name desc"

    name = fields.Char(string='Instance Name', required=True)
    host = fields.Char(string="Host", required=True)
    port = fields.Char(string="Port", required=True)
    user = fields.Char(string="User Name", required=True)
    password = fields.Char(string="Password", required=True)
    db_name = fields.Char(string="Oracle Database", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Close')],
        readonly=False, string='State', index=True , default='draft')

    def action_active(self):
        self.write({
            'state': 'active'
        })

    def try_connection(self):
        try:
            tusername = self.user
            tpasswrd = self.password
            thost = self.host
            tport = self.port
            tinstance = self.db_name
            conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
            cur = conn.cursor()
            if conn:
                self.write({
                    'state': 'active'
                })
            if conn:
                raise ValidationError('Successfully Connected')



        except Exception as e:
            raise ValidationError(e)

    def action_get_attendance_data(self):
        user_attendance = self.env['hr.user.attendance']
        attendance_ids = []
        conn = cx_Oracle.connect('xx_odoo/xxodoo123$@//10.8.8.191:1521/PROD')
        cur = conn.cursor()
        statement = 'select p.att_time AS timestamp, p.mac_number AS machine, p.card_no AS card, p.att_date AS attendance_date, p.creation_date AS creation_date, p.remarks AS remarks, p.updation_date AS updation_date from attend_data p where p.creation_date >= sysdate-3'
        cur.execute(statement)
        attendances = cur.fetchall()
        for attendance in attendances:
            duplicate_attendance = user_attendance.search([('card_no','=',attendance[2]),('time','=',attendance[0])], limit=1)
            if not duplicate_attendance:
            
                employee = self.env['hr.employee'].search([('barcode','=',attendance[2])], limit=1)
                timestamdata = attendance[6]
                timestamp1 = timestamdata.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S') - relativedelta(hours =+ 5) 
                attendance_data1 =  attendance[3]
                attendance_data = datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S')
                timedata = attendance[0]
                time = timedata     
                vals = {
                'timestamp': timestamp,
                'device_id': attendance[1],
                'employee_id': employee.id,
                'card_no': attendance[2],
                'attendance_date': attendance_data,
                'creation_date': attendance[4],
                'company_id': employee.company_id.id, 
                'remarks': attendance[5],
                'time':  attendance[0],
                'updation_date': attendance[6],
                }
                user_attendance= self.env['hr.user.attendance'].create(vals)
            
        









