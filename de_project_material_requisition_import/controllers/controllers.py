# # -*- coding: utf-8 -*-
from . import update
from . import config
import base64
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
import werkzeug
from werkzeug import urls
from werkzeug.exceptions import NotFound, Forbidden

from odoo import http, _
from odoo.http import request
from odoo.osv import expression
from odoo.tools import consteq, plaintext2html
from odoo.addons.mail.controllers.main import MailController
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError, UserError


def get_project(flag=0):
    projects = request.env['project.project'].search([('name', '=', 'Material Requisition')], limit=1)
    if projects:
        pass
    else:
        project_vals = {
            'name': 'Material Requisition'
        }
        projects = request.env['project.project'].sudo().create(project_vals)

    transfer_category = request.env['stock.transfer.order.category'].search([('is_publish','=', True)])
    transfer_types = request.env['stock.transfer.order.type'].search([('is_publish','=', True)])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'projects': projects,
        'categories': transfer_category,
        'transfer_types': transfer_types,
        'company_info': company_info,
        'tasks': tasks,
    }

def get_project_task(task):
    tasks = request.env['project.task'].search([('id','=',task.id)])
    return {
        'task': tasks,
    }

def get_transfer_category( type):

    projects = request.env['project.project'].search([('name','=', 'Material Requisition')], limit=1)
    if projects:
        pass
    else:
        project_vals = {
            'name': 'Material Requisition'
        }
        projects = request.env['project.project'].sudo().create(project_vals)

    transfer_category = request.env['stock.transfer.order.category'].search([('is_publish','=', True),('transfer_order_type_id','=',type)])
    transfer_types = request.env['stock.transfer.order.type'].search([('id','=', type)])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'projects': projects,
        'categories': transfer_category,
        'transfer_types': transfer_types,
        'company_info': company_info,
        'tasks': tasks,
    }

def get_transfer_transfer_category(category, transfer_id):
    projects = request.env['project.project'].search([('name', '=', 'Material Requisition')], limit=1)
    if projects:
        pass
    else:
        project_vals = {
            'name': 'Material Requisition'
        }
        projects = request.env['project.project'].sudo().create(project_vals)
    transfer_category = request.env['stock.transfer.order.category'].search(
        [('id', '=', category)], limit=1)
    transfer_types = request.env['stock.transfer.order.type'].search([('id', '=', transfer_id)])
    company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
    tasks = 'project.task'
    is_expiry_vals  = transfer_category.auto_expiry
    is_accidnent_vals = transfer_category.accident_report
    is_checklist_vals = transfer_category.hoto_checklist
    is_check_form_vals = transfer_category.health_check_form
    is_fir = transfer_category.fir_report
    return {
        'projects': projects.id,
        'categories': transfer_category,
        'transfer_types': transfer_types,
        'company_info': company_info,
        'user': company_info.id,
        'is_expiry_vals': is_expiry_vals,
        'is_accidnent_vals': is_accidnent_vals,
        'is_checklist_vals':  is_checklist_vals,
        'is_check_form_vals': is_check_form_vals,
        'is_fir': is_fir,
        'tasks': tasks,
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

class MaterialDocuments(http.Controller):



    @http.route('/material/document', type="http", website=True, auth='user')
    def portal_material_documents(self, **kw):
        return request.render("de_project_material_requisition_import.portal_material_documents_type", get_project())

    @http.route('/material/type', type="http", methods=['POST'], auth="public", website=True, csrf=False)
    def material_transfer_type(self, **kw):
        transfer_type = request.env['stock.transfer.order.type'].search([('name','=', kw.get('name'))], limit=1).id
        # transfer_id =  transfer_type.id
        return request.render("de_project_material_requisition_import.portal_material_documents_category", get_transfer_category(transfer_type))

    @http.route('/material/type/category', type="http", methods=['POST'], auth="public", website=True, csrf=False)
    def material_transfer_category(self, **kw):
        category = request.env['stock.transfer.order.category'].search([('id', '=', kw.get('transfer_category_id'))], limit=1).id
        transfer_id =  kw.get('type_id')
        return request.render("de_project_material_requisition_import.portal_material_documents_final",
                              get_transfer_transfer_category(category, transfer_id))



class CustomerPortal(CustomerPortal):


    def _task_get_page_view_values(self, task, next_id=0, pre_id=0, task_user_flag=0, access_token=None,
                                      **kwargs):
        company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
        values = {
            'page_name': 'task',
            'doc_task': task,
            'task_user_flag': task_user_flag,
            'next_id': next_id,
            'company_info': company_info,
            'pre_id': pre_id,
        }
        return self._get_page_view_values(task, access_token, values, 'task_history', False, **kwargs)

    @http.route(['/material/tasks', '/material/task/page/<int:page>'], type='http', auth="user", website=True)
    def portal_material_forms(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                           search_in='content', groupby=None, **kw):

        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'),
                    'domain': [('stage_id.name', 'in', ['new','done'])]},

            'draft': {'label': _('To Submit'), 'domain': [('stage_id.name', '=', 'new')]},
            'done': {'label': _('Done'), 'domain': [('stage_id.name', '=', 'done')]},
        }

        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Tasks')},
            'id': {'input': 'id', 'label': _('Search in Ref#')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        task_groups = request.env['project.task'].search([])

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

            # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            domain += search_domain
        task_count = request.env['project.task'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/material/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=555,
            page=page,
            step=self._items_per_page
        )

        _task = request.env['project.task'].search(domain, order=order, limit=self._items_per_page,
                                                  offset=pager['offset'])
        request.session['my_task_history'] = _task.ids[:100]

        grouped_tasks = [_task]

        paging(0, 0, 1)
        paging(grouped_tasks)
        company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'tasks',
            'default_url': '/material/tasks',
            'pager': pager,
            'company_info': company_info,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("de_project_material_requisition_import.portal_material_documents", values)

    @http.route(['/task/submit/<int:task_id>'], type='http', auth="public", website=True)
    def action_submit(self, task_id, access_token=None, **kw):
        id = task_id
        record = request.env['project.task'].sudo().browse(id)

        record.action_submit()
        try:
            task_sudo = self._document_check_access('project.task', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._task_get_page_view_values(task_sudo, **kw)
        return request.render("de_project_material_requisition_import.material_submited", {})


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'task_count' in counters:
            values['task_count'] = request.env['project.task'].search_count([])
        return values

    @http.route(['/material/task/<int:task_id>'], type='http', auth="user", website=True)
    def portal_material_form(self, task_id, access_token=None, **kw):

        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        next_id = 0
        pre_id = 0
        task_user_flag = 0

        task_id_list = paging(0, 1, 0)
        next_next_id = 0
        task_id_list.sort()
        length_list = len(task_id_list)
        length_list = length_list - 1
        if length_list != 0:
            if task_id in task_id_list:
                task_id_loc = task_id_list.index(task_id)
                if task_id_loc == 0:
                    next_id = 1
                    pre_id = 0
                elif task_id_loc == length_list:
                    next_id = 0
                    pre_id = 1
                else:
                    next_id = 1
                    pre_id = 1
        else:
            next_id = 0
            pre_id = 0

        values = self._task_get_page_view_values(task_sudo, next_id, pre_id, access_token, **kw)
        return request.render("de_project_material_requisition_import.portal_material_document_form", values)


