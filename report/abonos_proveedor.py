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

class ReportAbonosProveedor(models.AbstractModel):
    _name = 'report.maquilishuat.abonos_proveedor'

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
        facturas_compra = []
        totales = {'30':0,'mas':0,'total':0}
        # facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','in_invoice'),('state','in',['paid','open'])],order="date_invoice asc")
        pagos_ids = self.env['account.payment'].search([('payment_date','>=', fecha_inicio),('payment_date','<=',fecha_fin),('payment_type','=','outbound'),('state','in',['posted'])],order="payment_date asc")
        if pagos_ids:
            fecha_hoy = date.today()
            for pago in pagos_ids:
                if pago.invoice_ids:
                    diferencia_dias = pago.payment_date - pago.invoice_ids[0].date_invoice
                    dias = diferencia_dias.days
                    treinta = 0
                    mas = 0
                    total = 0
                    if dias <= 30:
                        treinta = pago.amount
                    elif dias > 30:
                        mas =  pago.amount
                    total = treinta + mas
                    pago_dic = {
                        'fecha_abono': pago.payment_date,
                        'fecha_comprobante': pago.invoice_ids[0].date_invoice,
                        'comprobante': pago.communication,
                        'proveedor': pago.partner_id.name,
                        'cheque': pago.name,
                        '30': treinta,
                        'mas': mas,
                        'total': total,
                    }
                    totales['30'] += treinta
                    totales['mas'] += mas
                    totales['total'] += total
                    facturas_compra.append(pago_dic)

        # if facturas_ids:
        #     fecha_hoy = date.today()
        #     for factura in facturas_ids:
        #         if factura.payment_ids:
        #             for pago in factura.payment_ids:
        #                 if pago.amount > 0:
        #                     diferencia_dias = pago.payment_date - factura.date_invoice
        #                     dias = diferencia_dias.days
        #                     treinta = 0
        #                     mas = 0
        #                     total = 0
        #                     if dias <= 30:
        #                         treinta = pago.amount
        #                     elif dias > 30:
        #                         mas =  pago.amount
        #                     total = treinta + mas
        #                     pago_dic = {
        #                         'fecha_abono': pago.payment_date,
        #                         'fecha_comprobante': factura.date_invoice,
        #                         'comprobante': pago.communication,
        #                         'factura': factura.reference,
        #                         'proveedor': factura.partner_id.name,
        #                         'cheque': pago.name,
        #                         '30': treinta,
        #                         'mas': mas,
        #                         'total': total,
        #                     }
        #                     totales['30'] += treinta
        #                     totales['mas'] += mas
        #                     totales['total'] += total
        #                     facturas_compra.append(pago_dic)

        return {'facturas_compra':facturas_compra, 'totales': totales}

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
