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

class ReportIngresosDiarios(models.AbstractModel):
    _name = 'report.maquilishuat.ingresos_diarios'

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
        formas_pago = {}
        total_general = {'credito': 0, 'contado':0, 'total':0, 'cuota_mensual': 0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['paid','open'])],order="date_invoice asc")
        if facturas_ids:
            for factura in facturas_ids:
                if factura.state == 'open' and factura.payment_ids:
                    for pago in factura.payment_ids:
                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 }  }
                        formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': pago.amount,'contado': 0,'total': pago.amount,'cuota_mensual': pago.amount})
                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0;
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;

                        total_general['credito'] +=pago.amount
                        total_general['contado'] +=0
                        total_general['total'] +=pago.amount
                        total_general['cuota_mensual'] +=pago.amount

                if factura.state == 'paid' and factura.payment_ids:
                    for pago in factura.payment_ids:
                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[],'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 } }
                        formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount})
                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0;
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] +=  pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;

                        total_general['credito'] += 0
                        total_general['contado'] += pago.amount
                        total_general['total'] +=pago.amount
                        total_general['cuota_mensual'] +=pago.amount
        # logging.warn(total_general)
        self._get_pagos(fecha_inicio,fecha_fin)
        return {'formas_pago':formas_pago.values(),'total_general': total_general}

    def _get_pagos(self,fecha_inicio,fecha_fin):
        formas_pago = {}
        total_general = {'credito': 0, 'contado':0, 'total':0, 'cuota_mensual': 0}
        pagos_ids = self.env['account.payment'].search([('payment_date','>=', fecha_inicio),('payment_date','<=',fecha_fin),('payment_type','=','inbound'),('state','in',['posted'])],order="payment_date asc")
        for pago in pagos_ids:
            for factura in pago.invoice_ids:
                if factura.state == 'open':
                    if pago.journal_id.name not in formas_pago:
                        formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 }  }

                    formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': pago.amount,'contado': 0,'total': pago.amount,'cuota_mensual': pago.amount})
                    formas_pago[pago.journal_id.name]['subtotal']['credito'] += pago.amount
                    formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0
                    formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount
                    formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;

                    total_general['credito'] +=pago.amount
                    total_general['contado'] +=0
                    total_general['total'] +=pago.amount
                    total_general['cuota_mensual'] +=pago.amount

                if factura.state == 'paid':
                    for pago in factura.payment_ids:
                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[],'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 } }
                        formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount})
                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0;
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] +=  pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount;
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;

                        total_general['credito'] += 0
                        total_general['contado'] += pago.amount
                        total_general['total'] +=pago.amount
                        total_general['cuota_mensual'] +=pago.amount
        logging.warn('PAGOS')
        logging.warn(formas_pago)
        return {'formas_pago':formas_pago.values(),'total_general': total_general}



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
            '_get_pagos': self._get_pagos,
            'fecha_actual': self.fecha_actual,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
