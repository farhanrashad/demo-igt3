# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Spare Penalty Report",
    "summary": "Spare Penalty Report",
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Warehouse',
    "version": "14.0.1.1.0",
    "depends": ["base","de_stock_material_transfer","report_xlsx"],
    "data": [
        'security/ir.model.access.csv',
        'wizards/spare_penalty_wizard.xml',
        'views/view_stock_transfer_order.xml',
        'reports/spare_penalty_report.xml'
    ],
    "installable": True,
}
