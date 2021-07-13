# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Employee Reporting",
    "category": 'HR',
    "summary": "This Module contain Following Reports"
               "\n1 Contract Expiry Report",
    "description": """
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '14.1.0.0',
    "depends": ['base', 'hr', 'report_xlsx', 'de_employee_enhancement'],
    # "depends": ['base', 'hr', 'report_xlsx', 'de_employee_overtime'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/contract_expiry_wizard_view.xml',
        'wizards/cost_center_wise_wizard_view.xml',
        'wizards/department_wise_wizard_view.xml',
        'views/hr_employee_report_menuitem.xml',
        'reports/contract_expiry_report_xlsx.xml',
        'reports/action_pdf_report.xml',
        'reports/contract_expiry_report_pdf.xml',
        'reports/cost_center_wise_report_pdf.xml',
        'reports/department_wise_report_pdf.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
