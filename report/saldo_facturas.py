# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from datetime import date
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import logging

class ReportSaldFacturas(models.AbstractModel):
    _name = 'report.maquilishuat.saldo_facturas'

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

    def factura_pagada_fecha_fin(self,factura,fecha_fin):
        total_pagado = 0
        dias = -1
        saldo = factura.amount_total
        logging.warn(factura)
        if factura.payment_ids:
            for p in factura.payment_ids:
                if p.payment_date > fecha_fin:
                    dias = (fecha_fin - factura.date_invoice)
                    total_pagado += p.amount
        else:
            dias = (fecha_fin - factura.date_invoice)
        return dias if dias == -1 else dias.days

    # Ordena por codigo
    def _get_facturas(self,fecha_inicio,fecha_fin):
        facturas = []
        totales = {'30': 0,'60': 0,'90': 0,'120': 0,'mas': 0,'total':0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['in_payment','open','paid'])],order="date_invoice asc")
        facturas_agrupadas = {}
        if facturas_ids:
            fecha_hoy = date.today()
            for factura in facturas_ids:
                treinta = 0
                sesenta = 0
                noventa = 0
                ciento_veinte = 0
                mas = 0
                # diferencia_dias = fecha_hoy - factura.date_invoice
                # dias = diferencia_dias.days
                dias = self.factura_pagada_fecha_fin(factura,datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').date())
                logging.warn(dias)
                if dias >=0:
                    if dias <= 30:
                        treinta = factura.amount_total
                    elif dias > 30 and dias <=60:
                        sesenta =  factura.amount_total
                    elif dias > 60 and dias <= 90:
                        noventa = factura.amount_total
                    elif dias > 90:
                        mas = factura.amount_total

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
                        'saldo_factura': factura.amount_total
                    }
                    totales['30'] += treinta
                    totales['60'] += sesenta
                    totales['90'] += noventa
                    totales['120'] += ciento_veinte
                    totales['mas'] += mas
                    totales['total'] += factura.amount_total
                    facturas.append(f)

        for f in facturas:
            codigo = f['codigo']
            if codigo not in facturas_agrupadas:
                facturas_agrupadas[codigo] = {
                                    'codigo': codigo,
                                    'nombre': f['nombre'],
                                    'grado': f['grado'],
                                    'numero': f['numero'],
                                    'fecha': f['fecha'],
                                    '30': 0,
                                    '60': 0,
                                    '90': 0,
                                    '120': 0,
                                    'mas': 0,
                                    'saldo_factura': 0}
            facturas_agrupadas[codigo]['30'] += f['30']
            facturas_agrupadas[codigo]['60'] += f['60']
            facturas_agrupadas[codigo]['90'] += f['90']
            facturas_agrupadas[codigo]['120'] += f['120']
            facturas_agrupadas[codigo]['mas'] += f['mas']
            facturas_agrupadas[codigo]['saldo_factura'] += f['saldo_factura']

        logging.warn(facturas_agrupadas.values())
        return {'fact':facturas_agrupadas.values(), 'suma_totales': totales}

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
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
