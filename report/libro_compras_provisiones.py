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

class ReportLibroComprasProvisiones(models.AbstractModel):
    _name = 'report.maquilishuat.libro_compras_provisiones'

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
        facturas_compra = {'credito_fiscal': {'lineas': {},'total_gravadas': 0,'total_exentas': 0,'total_iva':0,'total_total':0}, 'facturas': {'lineas': {},'total_gravadas': 0,'total_exentas': 0,'total_iva':0,'total_total':0}}
        totales = {'gravadas':0,'exentas':0, 'iva':0, 'total': 0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','in_invoice'),('state','in',['paid','open'])],order="date_invoice asc")

        if facturas_ids:
            fecha_hoy = date.today()
            for factura in facturas_ids:
                proveedor_id = factura.partner_id
                if factura.tipo_factura_compra == 'credito_fiscal':
                    if proveedor_id.id not in facturas_compra['credito_fiscal']['lineas']:
                        facturas_compra['credito_fiscal']['lineas'][proveedor_id.id] = {'fecha':factura.date_invoice,'referencia': factura.reference,'proveedor': proveedor_id.name,'gravadas':0,'excentas':0,'iva':0,'total':0}

                    for linea in factura.invoice_lince_ids:
                        gravada = 0
                        iva = 0
                        exentas = 0
                        if linea.invoice_line_tax_ids:
                            gravada = linea.price_subtotal
                            iva = linea.price_total - linea.price_subtotal
                            facturas_compra['credito_fiscal']['lineas'][proveedor_id.id]['gravadas'] += gravada
                            facturas_compra['credito_fiscal']['lineas'][proveedor_id.id]['iva'] += iva
                        else:
                            exentas = linea.price_total
                            facturas_compra['credito_fiscal']['lineas'][proveedor_id.id]['excentas'] += exentas

                        facturas_compra['credito_fiscal']['lineas'][proveedor_id.id]['total'] += gravada + iva + exentas

                        facturas_compra['credito_fiscal']['total_gravadas'] += gravada
                        facturas_compra['credito_fiscal']['total_exentas'] += exentas
                        facturas_compra['credito_fiscal']['total_iva'] += iva
                        facturas_compra['credito_fiscal']['total_total'] += gravada + iva + exentas

                        totales['gravadas'] += gravada
                        totales['exentas'] += exentas
                        totales['iva'] += iva
                        totales['total'] += gravada + iva + exentas

                else:
                    if proveedor_id.id not in facturas_compra['facturas']['lineas']:
                        facturas_compra['facturas']['lineas'][proveedor_id.id] = {'fecha':factura.date_invoice,'referencia': factura.reference,'proveedor': proveedor_id.name,'gravadas':0,'excentas':0,'iva':0,'total':0}


                    for linea in factura.invoice_lince_ids:
                        gravada = linea.price_total
                        iva = 0
                        exentas = 0
                        facturas_compra['facturas']['lineas'][proveedor_id.id]['gravadas'] += gravada

                        facturas_compra['facturas']['lineas'][proveedor_id.id]['total'] += gravada

                        facturas_compra['facturas']['total_gravadas'] += gravada
                        facturas_compra['facturas']['total_exentas'] += exentas
                        facturas_compra['facturas']['total_iva'] += iva
                        facturas_compra['facturas']['total_total'] += gravada + iva + exentas

                        totales['gravadas'] += gravada
                        totales['exentas'] += exentas
                        totales['iva'] += iva
                        totales['total'] += gravada + iva + exentas

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
