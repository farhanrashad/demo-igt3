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


def get_custom_entry(flag=0):
    projects = request.env['project.project'].search([])
    custom_entry_types = request.env['account.custom.entry.type'].search([])
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'projects': projects,
        'custom_entry_types': custom_entry_types,
        'company_info': company_info,
        'tasks': tasks,
    }

def get_custom_entry_final(entry_type):
    projects = request.env['project.project'].search([('name', '=', 'Third Party Billing')], limit=1)
    if not projects:
        vals = {
            'name': 'Third Party Billing',
        }
        projects = request.env['project.project'].search([], limit=1)

    custom_types = request.env['account.custom.entry.type'].search([('id', '=', entry_type)], limit=1)
    company_info = request.env['res.users'].search([('id','=',http.request.env.context.get('uid'))])
    tasks = 'project.task'
    return {
        'projects': projects.id,
        'entry_types': custom_types ,
        'partner': company_info.partner_id.id,
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
        entry_type = request.env['account.custom.entry.type'].search([('name', '=', kw.get('name'))], limit=1).id
        # transfer_id =  transfer_type.id
        return request.render("de_custom_journal_entry_import.portal_custom_entry_final",
                              get_custom_entry_final(entry_type))


class CustomerPortal(CustomerPortal):


    def _task_get_page_view_values(self, task, next_id=0, pre_id=0, task_user_flag=0, access_token=None,
                                      **kwargs):
        company_info = request.env['res.users'].search([('id', '=', http.request.env.context.get('uid'))])
        values = {
            'page_name': 'task',
            'entry_task': task,
            'task_user_flag': task_user_flag,
            'next_id': next_id,
            'company_info': company_info,
            'pre_id': pre_id,
        }
        return self._get_page_view_values(task, access_token, values, 'entry_history', False, **kwargs)

