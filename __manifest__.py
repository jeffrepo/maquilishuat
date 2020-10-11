# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Maquilishuat',
    'version': '11.0',
    'category': 'Maquilishuat',
    'sequence': 81,
    'summary': 'Desarrollo para colegio Maquilishuat',
    'description': """

       """,
    'website': 'sispav.com.gt',
    'depends': ['base','account'],
    'data': [
        'views/saldo_facturas_wizard.xml',
        # 'views/planilla.xml',
        # 'views/recibo_pago.xml',
        # 'views/report.xml',
        # 'views/hr_payroll_views.xml',
        # 'views/recibo_pago.xml',
        # 'views/hr_contract_views.xml',
        # 'views/hr_payroll_views.xml',
        # 'views/res_company_views.xml',
        # 'views/report.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
