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

class ReportEstadoCuentaCliente(models.AbstractModel):
    _name = 'report.maquilishuat.estado_cuenta_cliente'

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


    def estado_cuenta(self,fecha_inicio,fecha_fin,cliente_id):
        facturas_ids = self.env['account.invoice'].search([('id','=',cliente_id[0])],order="date_invoice asc")
        datos = {}
        logging.warn(facturas_ids)
        if facturas_ids:
            for f in facturas_ids:
                logging.warn(str(fecha_inicio))
                if str(f.date_invoice) >= str(fecha_inicio) and str(f.date_invoice) <= str(fecha_fin) and f.state in ['open','paid']:
                    if f.id not in datos:
                        datos[f.id] = {'codigo': f.partner_id.matricula,'cliente': f.partner_id.name, 'factura': f.number, 'cargos':0,'abonos':0,'saldos':0,'movimientos':[]}

                    saldo = 0
                    for m in f.move_id:
                        if saldo == 0:
                            saldo = m.debit - m.credit
                        else:
                            saldo -= m.debit - m.credit
                        datos[f.id]['movimientos'].append({'cargos': m.debit, 'abonos': m.credit, 'saldos':saldo})
        logging.warn(datos)
        return datos

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
        cliente_id = data.get('form', {}).get('cliente_id', False)
        # formato_planilla_id = data.get('form', {}).get('formato_planilla_id', False)
        docs = self.env[self.model].browse(docids)
        logging.warn(docs)


        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'fecha_fin': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'cliente_id': cliente_id,
            '_get_facturas': self._get_facturas,
            'fecha_actual': self.fecha_actual,
            'estado_cuenta': self.estado_cuenta,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
