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

class ReportKardexProducto(models.AbstractModel):
    _name = 'report.maquilishuat.kardex_producto'

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

    def _get_kardex(self,fecha_inicio,fecha_fin,productos_ids):
        logging.warn(productos_ids)
        movimientos = self.env['stock.move.line'].search([('date','>=', fecha_inicio),('date','<=',fecha_fin),('pickin_id','!=',False),('product_id','in',productos_ids)])
        movimientos_productos = {}
        if movimientos:
            for m in movimientos:
                if m.product_id.id not in movimientos_productos:
                    movimientos_productos[m.product_id.id] = {'nombre': m.product_id.name,'stock_move_line': []}
                movimientos_productos[m.product_id.id]['stock_move_line'].append({
                    'documento': m.reference,
                    'fecha': m.date,
                    'proveedor': m.pickin_id.partner_id.name if (m.pickin_id and m.pickin_id.partner_id) else '',
                    'costo_promedio': 1
                })
            logging.warn(movimientos)
        return True

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
        productos_ids = data.get('form', {}).get('productos_ids', False)
        # formato_planilla_id = data.get('form', {}).get('formato_planilla_id', False)
        docs = self.env[self.model].browse(docids)
        logging.warn(docs)


        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'fecha_fin': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'productos_ids': productos_ids,
            '_get_kardex': self._get_kardex,
            'fecha_actual': self.fecha_actual,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
