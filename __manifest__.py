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
        'data/paperformats.xml',
        'views/colegiaturas_pendientes.xml',
        'views/colegiaturas_pendientes_wizard.xml',
        'views/libro_ventas_cf.xml',
        'views/libro_ventas_cf_wizard.xml',
        'views/libro_ventas_contribuyente.xml',
        'views/libro_ventas_contribuyente_wizard.xml',
        'views/libro_ventas_cf_detallado.xml',
        'views/libro_ventas_cf_detallado_wizard.xml',
        'views/libro_compras.xml',
        'views/libro_compras_wizard.xml',
        'views/ventas_item.xml',
        'views/ventas_item_wizard.xml',
        'views/ingreso_detallado_cliente.xml',
        'views/ingreso_detallado_cliente_wizard.xml',
        'views/colegiaturas_pagadas_no.xml',
        'views/colegiaturas_pagadas_no_wizard.xml',
        'views/estado_cuenta_cliente.xml',
        'views/estado_cuenta_cliente_wizard.xml',
        'views/ventas.xml',
        'views/ventas_wizard.xml',
        'views/saldo_facturas.xml',
        'views/abonos_cuentas_cobrar.xml',
        'views/ingresos_diarios.xml',
        'views/ingresos_diarios_wizard.xml',
        'views/abonos_cuentas_cobrar_wizard.xml',
        'views/saldo_facturas_wizard.xml',
        'views/account_invoice_view.xml',
        'views/sale_views.xml',
        'views/account_payment_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
