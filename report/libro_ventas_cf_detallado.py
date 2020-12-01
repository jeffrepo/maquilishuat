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

class ReportLibroVentasCFDetallado(models.AbstractModel):
    _name = 'report.maquilishuat.libro_ventas_cf_detallado'

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

    def _get_facturas(self,fecha_inicio,fecha_fin):
        facturas = []
        totales = {'exentas': 0,'gravadas': 0,'total': 0,'valor':0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['open','paid'])],order="date_invoice asc")

        if facturas_ids:
            for f in facturas_ids:
                exentas = 0
                gravadas = 0
                valor = 0
                for linea in f.invoice_line_ids:
                    if linea.invoice_line_tax_ids:
                        gravadas += linea.price_subtotal
                        valor += (linea.price_total - linea.price_subtotal)
                    else:
                        exentas += linea.price_total

                dic = {
                    'fecha': f.date_invoice,
                    'comprobante': f.number,
                    'cliente': f.partner_id.name,
                    'exentas': exentas,
                    'gravadas': gravadas,
                    'total': exentas + gravadas,
                    'valor': valor,
                }
                facturas.append(dic)
                totales['exentas'] += exentas
                totales['gravadas'] += gravadas
                totales['total'] += exentas + gravadas
                totales['valor'] += valor
        logging.warn('FACTURAS')
        logging.warn(facturas)
        return {'fact':facturas, 'suma_totales': totales}

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
            '_get_facturas': self._get_facturas,
            'fecha_actual': self.fecha_actual,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
