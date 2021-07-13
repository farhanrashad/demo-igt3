# -*- coding: utf-8 -*-

from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from datetime import date, datetime, timedelta
from operator import itemgetter
from datetime import datetime , date
from odoo import exceptions
from dateutil.relativedelta import relativedelta


from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR

def attendance_page_content(flag = 0):
    emps = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])

    return {
        'emps': emps,
        'success_flag' : flag,
    }



def paging(data, flag1 = 0, flag2 = 0):        
    if flag1 == 1:
        return config.list12
    elif flag2 == 1:
        config.list12.clear()
    else:
        k = []
        for rec in data:
            for ids in rec:
                config.list12.append(ids.id)  
                
        
class CreateAttendance(http.Controller):
    @http.route('/hr/attendance/rectify/',type="http", website=True, auth='user')
    def approvals_create_template(self, **kw):
       return request.render("de_portal_attendance.attendance_create_rectify", attendance_page_content())
    
    
    @http.route('/hr/attendance/rectify/save', type="http", auth="public", website=True)
    def create_expenses(self, **kw):
        checkin_date_in = kw.get('check_in')
        if checkin_date_in:
            date_processing_in = checkin_date_in.replace('T', '-').replace(':', '-').split('-')
            date_processing_in = [int(v) for v in date_processing_in]
            checkin_date_out = datetime(*date_processing_in)
            attendance_data_in = datetime(*date_processing_in) - relativedelta(hours =+ 5)  
            
            if attendance_data_in.date() > date.today():
                return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
            
        checkout_date_in = kw.get('check_out') 
        if checkout_date_in:
            date_processing_out = checkout_date_in.replace('T', '-').replace(':', '-').split('-')
            date_processing_out = [int(v) for v in date_processing_out]
            checkout_date_out = datetime(*date_processing_out)
            attendance_data_out = datetime(*date_processing_out) - relativedelta(hours =+ 5)
            
            if attendance_data_out.date() > date.today():
                return request.render("de_portal_attendance.cannot_submit_future_days_commitment_msg", attendance_page_content())
            
        if kw.get('id'):
            exist_attendance1 = request.env['hr.attendance'].search([('id','=',int(kw.get('id')))])
            if not kw.get('check_out'):
                check_out =  exist_attendance1.check_out
                
                expense_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  attendance_data_in,
                    'check_out': check_out,
                    'date':  check_out,
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(expense_val)
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
            elif not kw.get('check_in'):
                check_in =  exist_attendance1.check_in
                
                expense_val = {
                    'reason': kw.get('description'),
                    'employee_id': int(kw.get('employee_id')),
                    'check_in':  check_in,
                    'check_out': attendance_data_out,
                    'date':  check_in,
                    'attendance_id':  int(kw.get('id')),
                }
                record = request.env['hr.attendance.rectification'].sudo().create(expense_val)
                record.action_submit()
                return request.render("de_portal_attendance.rectification_submited", {})
                
        else: 
            expense_val = {
                'reason': kw.get('description'),
                'employee_id': int(kw.get('employee_id')),
                'check_in':  attendance_data_in,
                'check_out': attendance_data_out,
                'date':  attendance_data_in,
            }
            record = request.env['hr.attendance.rectification'].sudo().create(expense_val)
            record.action_submit()
            return request.render("de_portal_attendance.rectification_submited", {})
    
    
    
   


class CustomerPortal(CustomerPortal):
    
    
    @http.route(['/hr/attendance/cancel/<int:attendance_id>'], type='http', auth="public", website=True)
    def action_cancel(self,attendance_id , access_token=None, **kw):
        id=attendance_id
        rectification = request.env['hr.attendance.rectification'].sudo().browse(id)

        rectification.action_refuse()
        try:
            rectification_sudo = self._document_check_access('hr.attendance.rectification', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._attendance_get_page_view_values(rectification_sudo, **kw) 
        return request.render("de_portal_attendance.rectification_cancel", {})
    
    
    @http.route(['/hr/attendance/rectify/<int:attendance_id>'], type='http', auth="public", website=True)
    def attendance_edit_template(self,attendance_id, access_token=None ,**kw):
        id = attendance_id
        try:
            expense_sudo = self._document_check_access('hr.attendance', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._attendance_get_page_view_values(expense_sudo, **kw) 
        exist_attendance = request.env['hr.attendance'].sudo().browse(id)
        employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))])
        checkin_date_in = str(exist_attendance.check_in)
        date_processing_in = checkin_date_in.replace(':', '-').replace('T', '-').split('-')
        checkout_date_in = str(exist_attendance.check_out) 
        date_processing_out = checkout_date_in.replace(':', '-').replace('T', '-').split('-')
        values.update({
            'exist_attendance': exist_attendance,
            'date_processing_in': date_processing_in,
            'date_processing_out': date_processing_out,
             'emps' : employees,
        })
        return request.render("de_portal_attendance.attendance_rectify", values) 
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'attendance_count' in counters:
            values['attendance_count'] = request.env['hr.attendance'].search_count([])
        return values
  
    def _attendance_get_page_view_values(self,attendance, next_id = 0,pre_id= 0, attendance_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'Attendance',
            'attendance' : attendance,
            'attendance_user_flag': attendance_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(attendance, access_token, values, 'my_attendance_history', False, **kwargs)

    @http.route(['/hr/attendances', '/hr/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_hr_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                         search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'id': {'label': _('Default'), 'order': 'id asc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'employee_id desc' },
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
                                                
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
           
        searchbar_inputs = {
            'id': {'input': 'id', 'label': _('Search in No#')},
            'employee_id.name': {'input': 'employee_id.name', 'label': _('Search in Employee')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        date = fields.date.today() - timedelta(30)
        project_groups = request.env['hr.attendance'].search([('check_in','>=', date)])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
#         domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]       

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'ID'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('employee_id.name', 'Employee'):
                search_domain = OR([search_domain, [('employee_id.name', 'ilike', search)]])
            domain += search_domain
 
        attendance_count = request.env['hr.attendance'].search_count(domain)

        pager = portal_pager(
            url="/hr/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        _attendances = request.env['hr.attendance'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_attendance_history'] = _attendances.ids[:100]

        grouped_attendances = [project_groups]
                
        paging(0,0,1)
        paging(grouped_attendances)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_attendances': grouped_attendances,
            'page_name': 'attendance',
            'default_url': '/hr/attendances',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_portal_attendance.portal_hr_attendances", values)   

   
    @http.route(['/hr/attendance/<int:attendance_id>'], type='http', auth="user", website=True)
    def portal_hr_attendance(self, attendance_id, access_token=None, **kw):
        values = []

        id = attendance_id
        try:
            attendance_sudo = self._document_check_access('hr.attendance', attendance_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        next_id = 0
        pre_id = 0
        attendance_user_flag = 0

                
        attendance_id_list = paging(0,1,0)
        next_next_id = 0
        attendance_id_list.sort()
        length_list = len(attendance_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if attendance_id in attendance_id_list:
                attendance_id_loc = attendance_id_list.index(attendance_id)
                if attendance_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif attendance_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0

        values = self._attendance_get_page_view_values(attendance_sudo,next_id, pre_id, attendance_user_flag,access_token, **kw) 
        return request.render("de_portal_attendance.portal_hr_attendance", values)

    @http.route(['/attendance/next/<int:attendance_id>'], type='http', auth="user", website=True)
    def portal_my_next_attendance(self, attendance_id, access_token=None, **kw):
        
        attendance_id_list = paging(0,1,0)
        next_next_id = 0
        attendance_id_list.sort()
        
        length_list = len(attendance_id_list)
        if length_list == 0:
            return request.redirect('/hr')
        length_list = length_list - 1
        
        if attendance_id in attendance_id_list:
            attendance_id_loc = attendance_id_list.index(attendance_id)
            next_next_id = attendance_id_list[attendance_id_loc + 1] 
            next_next_id_loc = attendance_id_list.index(next_next_id)
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in attendance_id_list:
                if ids < attendance_id:
                    buffer_smaller = ids
                if ids > attendance_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_larger:
                next_next_id = buffer_smaller
            elif buffer_smaller:
                next_next_id = buffer_larger
                
            next_next_id_loc = attendance_id_list.index(next_next_id)
            length_list = len(attendance_id_list)
            length_list = length_list + 1
            if next_next_id_loc == length_list:
                next_id = 0
                pre_id = 1
            elif next_next_id_loc == 0:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1
         
        values = []

        id = attendance_id
        try:
            attendance_sudo = self._document_check_access('hr.attendance', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        attendance_user_flag = 0


        values = self._attendance_get_page_view_values(attendance_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_portal_attendance.portal_hr_attendance", values)

  
    @http.route(['/attendance/pre/<int:attendance_id>'], type='http', auth="user", website=True)
    def portal_my_pre_attendance(self, attendance_id, access_token=None, **kw):
        
        attendance_id_list = paging(0,1,0)
        pre_pre_id = 0
        attendance_id_list.sort()
        length_list = len(attendance_id_list)
    
        if length_list == 0:
            return request.redirect('/my')
        
        length_list = length_list - 1
        if attendance_id in attendance_id_list:
            attendance_id_loc = attendance_id_list.index(attendance_id)
            pre_pre_id = attendance_id_list[attendance_id_loc - 1] 
            pre_pre_id_loc = attendance_id_list.index(attendance_id)

            if attendance_id_loc == 1:
                next_id = 1
                pre_id = 0
            else:
                next_id = 1
                pre_id = 1      
        else:
            buffer_larger = 0
            buffer_smaller = 0
            buffer = 0
            for ids in attendance_id_list:
                if ids < attendance_id:
                    buffer_smaller = ids
                if ids > attendance_id:
                    buffer_smaller = ids
                if buffer_larger and buffer_smaller:
                    break
            if buffer_smaller:
                pre_pre_id = buffer_smaller
            elif buffer_larger:
                pre_pre_id = buffer_larger
                
            pre_pre_id_loc = attendance_id_list.index(pre_pre_id)
            length_list = len(attendance_id_list)
            length_list = length_list -1
            if pre_pre_id_loc == 0:
                next_id = 1
                pre_id = 0
            elif pre_pre_id_loc == length_list:
                next_id = 0
                pre_id = 1
            else:
                next_id = 1
                pre_id = 1
   
        values = []

        id = pre_pre_id
        try:
            attendance_sudo = self._document_check_access('hr.attendance', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        attendance_user_flag = 0


        values = self._attendance_get_page_view_values(attendance_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_portal_attendance.portal_hr_attendance", values)

    