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

class ReportVentasItem(models.AbstractModel):
    _name = 'report.maquilishuat.ventas_item'

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
        totales = {'30': 0,'60': 0,'90': 0,'120': 0,'mas': 0,'total':0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['in_payment','open'])],order="date_invoice asc")

        if facturas_ids:
            fecha_hoy = date.today()
            for factura in facturas_ids:
                treinta = 0
                sesenta = 0
                noventa = 0
                ciento_veinte = 0
                mas = 0
                diferencia_dias = fecha_hoy - factura.date_invoice
                dias = diferencia_dias.days
                if dias <= 30:
                    treinta = factura.residual
                elif dias > 30 and dias <=60:
                    sesenta =  factura.residual
                elif dias > 60 and dias <= 90:
                    noventa = factura.residual
                elif dias > 90:
                    mas = factura.residual

                f = {
                    'codigo': factura.partner_id.matricula,
                    'nombre': factura.partner_id.name,
                    'grado': factura.grado_id.nombre if factura.grado_id else '',
                    'numero': factura.name,
                    'fecha': factura.date_invoice,
                    '30': treinta,
                    '60': sesenta,
                    '90': noventa,
                    '120': ciento_veinte,
                    'mas': mas,
                    'saldo_factura': factura.residual
                }
                totales['30'] += treinta
                totales['60'] += sesenta
                totales['90'] += noventa
                totales['120'] += ciento_veinte
                totales['mas'] += mas
                totales['total'] += factura.residual
                facturas.append(f)
        return {'fact':facturas, 'suma_totales': totales}

    def _get_facturas_anticipadas(self,fecha_inicio,fecha_fin):
        datos = {}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=',fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['paid'])],order="date_invoice asc")
        if facturas_ids:
            for factura in facturas_ids:
                for linea in factura.invoice_line_ids:
                    if 'MENSUAL ANTICIPADO' in linea.name:
                        if linea.product_id.id not in datos:
                            datos[linea.product_id] = {'item': linea.product_id.name, 'anticipos':[]}
                        datos[linea.product_id]['anticipos'].append({'numero': factura.number,'fecha': factura.date_invoice,'descripcion': linea.name,'cantidad': linea.quantity,'precio_unitario': linea.price_unit, 'ventas_exentas': linea.price_total, 'ventas_gravadas': 0})
        return {'fac':datos.values(),'venta_total':0}

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
            '_get_facturas_anticipadas': self._get_facturas_anticipadas,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
