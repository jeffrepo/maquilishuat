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

class ReportProductoFamilia(models.AbstractModel):
    _name = 'report.maquilishuat.producto_familia'

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

    def _get_listado_producto(self,fecha_inicio,fecha_fin,uniformes,libros):
        productos_ids = self.env['product.product'].search([],order='default_code asc')
        logging.warn('productos')
        logging.warn(productos_ids)
        productos_lista = []
        if productos_ids:
            if libros:
                for p in productos_ids:
                    logging.warn(p.categ_id.parent_id)
                    if p.categ_id and p.categ_id.parent_id and 'LIBROS' in p.categ_id.parent_id.name:
                        # cantidad_existencia = p.with_context(company_owned=True, owner_id=False).qty_available
                        cantidad_existencia = p._compute_quantities_dict(False, False, False, fecha_inicio, fecha_fin)
                        logging.warn('cantidad existencias')
                        logging.warn(cantidad_existencia)
                        if cantidad_existencia > 0:
                            costo = p.get_history_price(self.env.user.company_id.id, date=fecha_fin)
                            valor = cantidad_existencia * costo
                            productos_lista.append({'codigo': p.default_code,'nombre':p.name,'costo': costo,'existencia': existencia, 'valor': 1})
            #
            # if uniformes:


            # for m in movimientos:
            #     if m.product_id.id not in movimientos_productos:
            #         movimientos_productos[m.product_id.id] = {'nombre': str(m.product_id.default_code) +' '+str(m.product_id.name),'stock_move_line': []}
            #     precio_costo_salida = m.product_id.get_history_price(
            #         self.env.user.company_id.id,
            #         date=m.date,
            #     )
            #     movimientos_productos[m.product_id.id]['stock_move_line'].append({
            #         'documento': m.reference,
            #         'fecha': m.date,
            #         'proveedor': m.picking_id.partner_id.name if (m.picking_id and m.picking_id.partner_id) else '',
            #         'costo_promedio': m.product_id.standard_price,
            #         'cantidad_entrada': m.qty_done if m.location_dest_id.usage != 'customer' else 0,
            #         'costo_entrada': precio_costo_salida,
            #         'cantidad_salidas': m.qty_done if m.location_dest_id.usage == 'customer' else 0,
            #         'costo_salidas': precio_costo_salida,
            #         'cantidad_existencia': m.product_id.with_context(company_owned=True, owner_id=False).qty_available,
            #         'costo_actual': m.product_id.standard_price
            #     })
        #     logging.warn(movimientos)
        #
        # logging.warn(movimientos_productos)
        return productos_lista

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
            '_get_listado_producto': self._get_listado_producto,
            'fecha_actual': self.fecha_actual,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
