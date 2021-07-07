# -*- coding: utf-8 -*-

from . import config
from . import update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import OrderedDict
from operator import itemgetter
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR


employee_list_attendance = []

def site_attendance_page_content(flag = 0): 
    global employee_list_attendance
    employees = request.env['hr.employee'].search([('site_incharge_id.user_id','=',http.request.env.context.get('uid'))])
    return {
        'emps': employees,
        'employee_list': employee_list_attendance,
        'success_flag' : flag,
    }


def stringToList(string):
    listRes = list(string.split(" "))
    return listRes



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
    @http.route('/hr/site/attendance/create/',type="http", website=True, auth='user')
    def approvals_create_template(self, **kw):
        global employee_list_attendance
        employee_list_attendance = []
        return request.render("de_site_attendance.portal_create_site_attendances", site_attendance_page_content())
    
    
    
  
   
    
    
    
    
    @http.route('/hr/site/attendance/save', type="http", auth="public", website=True)
    def create_site_attendance(self, **kw):
        list = []
        employees = request.env['hr.employee'].search([('user_id','=',http.request.env.context.get('uid'))], limit=1)
        workers = request.env['hr.employee'].search([('site_incharge_id.user_id','=',http.request.env.context.get('uid'))], limit=1)
        global employee_list_attendance
        
        siteattendane_val = {
            'incharge_id': employees.id,
            'date_from': kw.get('date_from'),
            'date_to':  kw.get('date_to'),
            'attendance_line_ids': kw.get('unit_expense'),
        }
        record = request.env['hr.attendance.site'].sudo().create(siteattendane_val)
        for worker in employee_list_attendance:
            line_vals = {
                'site_id': record.id,
                'employee_id': worker['employee_id'],
                'days': worker['days'],
                'normal_overtime': worker['normal_overtime'],
                'gazetted_overtime':  worker['gazetted_overtime'],
                }
            record_lines = request.env['hr.attendance.site.line'].sudo().create(line_vals)
        employee_list_attendance = []
        return request.render("de_site_attendance.site_attendane_submited", {})
    
    
    
    @http.route('/hr/site/attendance/line/save', type="http", auth="public", website=True)
    def create_site_attendance_line(self, **kw):
        global employee_list_attendance
        emp = request.env['hr.employee'].search([('id','=',int(kw.get('employee_id')))], limit=1)
        line_vals = {
                'employee_id': int(kw.get('employee_id')),
                'name': emp.name,
                'days':  int(kw.get('total_days')),
                'normal_overtime':  float(kw.get('normal_overtime')),
                'gazetted_overtime':  float(kw.get('gazetted_overtime')),
                }
        employee_list_attendance.append(line_vals)
        return request.render("de_site_attendance.portal_create_site_attendances", site_attendance_page_content())
    
    
    
   


class CustomerPortal(CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'site_attendance_count' in counters:
            values['site_attendance_count'] = request.env['hr.attendance.site'].search_count([])
        return values
  
    def _site_attendance_get_page_view_values(self,site_attendance, next_id = 0,pre_id= 0, site_attendance_user_flag = 0, access_token = None, **kwargs):
        values = {
            'page_name' : 'Site Attendance',
            'site_attendance' : site_attendance,
            'attendance_user_flag': site_attendance_user_flag,
            'next_id' : next_id,
            'pre_id' : pre_id,
        }
        return self._get_page_view_values(site_attendance, access_token, values, 'my_site_attendance_history', False, **kwargs)

    @http.route(['/hr/site/attendances', '/hr/site/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_hr_site_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
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

        project_groups = request.env['hr.attendance.site'].search([])

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
 
        attendance_count = request.env['hr.attendance.site'].search_count(domain)

        pager = portal_pager(
            url="/hr/site/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'seissuesarch_in': search_in, 'search': search},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        _attendances = request.env['hr.attendance.site'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_attendance_history'] = _attendances.ids[:100]

        grouped_site_attendances = [_attendances]
                
        paging(0,0,1)
        paging(grouped_site_attendances)
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_site_attendance': grouped_site_attendances,
            'page_name': 'siteattendance',
            'default_url': '/hr/site/attendances',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_site_attendance.portal_hr_site_attendances", values)   

   
    @http.route(['/hr/site/attendance/<int:site_attendance_id>'], type='http', auth="user", website=True)
    def portal_hr_site_attendance(self, site_attendance_id, access_token=None, **kw):
        values = []

        id = site_attendance_id
        try:
            attendance_sudo = self._document_check_access('hr.attendance.site', id, access_token)
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
            if site_attendance_id in attendance_id_list:
                attendance_id_loc = attendance_id_list.index(site_attendance_id)
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

        values = self._site_attendance_get_page_view_values(attendance_sudo,next_id, pre_id, attendance_user_flag,access_token, **kw) 
        return request.render("de_site_attendance.portal_hr_site_attendance", values)

    @http.route(['/site/attendance/next/<int:attendance_id>'], type='http', auth="user", website=True)
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
            attendance_sudo = self._document_check_access('hr.attendance.site', next_next_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        attendance_user_flag = 0


        values = self._site_attendance_get_page_view_values(attendance_sudo,next_id, pre_id, access_token, **kw) 
        return request.render("de_site_attendance.portal_hr_site_attendance", values)

  
    @http.route(['/site/attendance/pre/<int:attendance_id>'], type='http', auth="user", website=True)
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
            attendance_sudo = self._document_check_access('hr.attendance.site', pre_pre_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        

        attendance_user_flag = 0


        values = self._site_attendance_get_page_view_values(attendance_sudo, next_id,pre_id, access_token, **kw) 
        return request.render("de_site_attendance.portal_hr_site_attendance", values)

    