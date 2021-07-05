# -*- coding: utf-8 -*-
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


def get_custom_entry(flag=0):
    entry_type_list = []
    custom_entry_types = request.env['account.custom.entry.type'].search([('is_publish','=',True)])
    for entry in custom_entry_types:
        for group in entry.group_id.users:
            if group.id == http.request.env.context.get('uid'):
                entry_type_list.append(entry.id) 

    allow_custom_entry_types = request.env['account.custom.entry.type'].search([('id', 'in', entry_type_list)])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'custom_entry_types': allow_custom_entry_types,
        'company_info': company_info,
        'tasks': tasks,
    }

def get_custom_entry_final(entry_type):


    custom_types = request.env['account.custom.entry.type'].search([('id', '=', entry_type)], limit=1)
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'entry_types': custom_types ,
        'partner': company_info.partner_id.id,
        'user': company_info.id,
        'title': custom_types.name +' '+ str(company_info.partner_id.name) +' '+ str(fields.date.today()),
        'company_info': company_info,
        'tasks': tasks,
    }


def get_custom_entry_final_update(entry_type, entry):


    custom_entry = request.env['account.custom.entry'].search([('id', '=', entry)], limit=1)
    custom_types = request.env['account.custom.entry.type'].search([('id', '=', entry_type)], limit=1)
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'entry_types': custom_types ,
        'partner': company_info.partner_id.id,
        'custom_entry': custom_entry.id, 
        'user': company_info.id,
        'title': custom_types.name +' '+ str(company_info.partner_id.name) +' '+ str(fields.date.today()),
        'company_info': company_info,
        'tasks': tasks,
    }


def get_project_task(task):
    tasks = request.env['project.task'].search([('id','=',task.id)])
    return {
        'task': tasks,
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

class CustomEntry(http.Controller):



    @http.route('/custom/entry', type="http", website=True, auth='user')
    def portal_custom_entry_task(self, **kw):
        return request.render("de_custom_journal_entry_import.portal_custom_entry_type", get_custom_entry())

    @http.route('/entry/type', type="http", methods=['POST'], auth="public", website=True, csrf=False)
    def custom_entry_type(self, **kw):
        entry_types = request.env['account.custom.entry.type'].search([('id', '=', kw.get('entry_type_id'))], limit=1).id
        
        return request.render("de_custom_journal_entry_import.portal_custom_entry_final",
                              get_custom_entry_final(entry_types))
    
    
    
    @http.route('/entry/type/update', type="http", methods=['POST'], auth="public", website=True, csrf=False)
    def custom_entry_type_update(self, entry, **kw):
        if entry:            
           entry_types = request.env['account.custom.entry'].search([('id', '=', entry)], limit=1).custom_entry_type_id.id
        else:
            entry_types = request.env['account.custom.entry.type'].search([('name', '=', kw.get('name'))], limit=1).id
        return request.render("de_custom_journal_entry_import.portal_custom_entry_final_update",
                              get_custom_entry_final_update(entry_types, entry))
    


class CustomerPortal(CustomerPortal):


    def _task_get_page_view_values(self, task, next_id=0, pre_id=0, task_user_flag=0, access_token=None,
                                      **kwargs):
        company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
        projects = request.env['project.project'].search([('name', '=', 'Third Party Billing')], limit=1)
        if not projects:
            vals = {
                'name': 'Third Party Billing',
            }
            projects = request.env['project.project'].search([], limit=1)

        custom_entry = request.env['account.custom.entry'].search([('id', '=', task.id)], limit=1)
        custom_types = request.env['account.custom.entry.type'].search([], limit=1)
        company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
        tasks = 'project.task'
        values = {
            'projects': projects.id,
            'entry_types': custom_types.id ,
            'partner': company_info.partner_id.id,
            'custom_entry': custom_entry, 
            'user': company_info.id,
            'title': custom_types.name +' '+ str(company_info.partner_id.name) +' '+ str(fields.date.today()),
            'company_info': company_info,
            'tasks': tasks,
        }
    
        return self._get_page_view_values(task, access_token, values, 'entry_history', False, **kwargs)
    
    
    
    @http.route(['/entry/type/update/<int:custom_id>'],   type='http', auth="public", website=True)
    def action_custom_entry_update(self,custom_id , access_token=None, **kw):
        entry=custom_id
        custom_entry = request.env['account.custom.entry'].sudo().browse(entry)
        CustomEntry.custom_entry_type_update(self, entry)
        try:
            custom_sudo = self._document_check_access('account.custom.entry', entry, access_token)
            CustomEntry.custom_entry_type_update(self, entry)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        
        return  CustomEntry.custom_entry_type_update(self, entry)
