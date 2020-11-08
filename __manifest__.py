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
    'depends': ['base','account','colegio','sale'],
    'data': [
        'views/saldo_facturas.xml',
        'views/saldo_facturas_wizard.xml',
        'views/account_invoice_view.xml',
        'views/sale_views.xml',
        'views/account_payment_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
