# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from datetime import date
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import pytz
import logging

class ReportColegiaturasPendientes(models.AbstractModel):
    _name = 'report.maquilishuat.colegiaturas_pendientes'

    def mes_letras(self,fecha):
        mes_nomina = int(datetime.datetime.strptime(str(fecha), '%Y-%m-%d').date().strftime('%m'))
        mes =  ''
        if mes_nomina == 1:
            mes = 'ENERO'
        if mes_nomina == 2:
            mes = 'FEBRERO'
        if mes_nomina == 3:
            mes = 'MARZO'
        if mes_nomina == 4:
            mes = 'ABRIL'
        if mes_nomina == 6:
            mes = 'MAYO'
        if mes_nomina == 6:
            mes = 'JUNIO'
        if mes_nomina == 7:
            mes = 'JULIO'
        if mes_nomina == 8:
            mes = 'AGOSTO'
        if mes_nomina == 9:
            mes = 'SEPTIEMBRE'
        if mes_nomina == 10:
            mes = 'OCTUBRE'
        if mes_nomina == 11:
            mes = 'NOVIEMBRE'
        if mes_nomina == 12:
            mes = 'DICIEMBRE'
        return mes


    def get_clientes(self,fecha_inicio,fecha_fin):
        clientes_facturar = {}

        facturas = self.env['account.invoice'].search([('date_invoice','>=',fecha_inicio),('date_invoice','<=',fecha_fin)])
        clientes = self.env['res.partner'].search([('grado_id','!=',False),('customer','=',True)])

        clientes_facturas = []
        for factura in facturas:
            clientes_facturas.append(factura.partner_id.id)

        for cliente in clientes:
            if cliente.id not in clientes_facturas:
                if cliente.grado_id.id not in clientes_facturar:
                    clientes_facturar[cliente.grado_id.id] = {'grado': cliente.grado_id.nombre, 'clientes': []}
                clientes_facturar[cliente.grado_id.id]['clientes'].append(cliente)

        logging.warn('get clientes')
        logging.warn(clientes_facturar)
        return clientes_facturar.values()

    def fecha_actual(self):
        logging.warn(datetime.datetime.now())

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hora = datetime.datetime.now().astimezone(timezone).strftime('%d/%m/%Y')
        logging.warn(fecha_hora)
        return fecha_hora

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = 'account.invoice'
        fecha_fin = data.get('form', {}).get('fecha_fin', False)
        fecha_inicio = data.get('form', {}).get('fecha_inicio', False)
        # formato_planilla_id = data.get('form', {}).get('formato_planilla_id', False)
        docs = self.env[self.model].browse(docids)
        logging.warn(docs)


        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'fecha_fin': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'fecha_actual': self.fecha_actual,
            'get_clientes': self.get_clientes,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
