# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import base64
import xlsxwriter
import io
import logging
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime

class saldo_facturas_wizard(models.TransientModel):
    _name = 'maquilishuat.saldo_facturas.wizard'

    archivo = fields.Binary('Archivo')
    name =  fields.Char('File Name', size=32)
    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')

    def factura_pagada_fecha_fin(self,factura,fecha_fin):
        total_pagado = 0
        dias = -1
        saldo = factura.amount_total
        # logging.warn(factura)
        # residual_factura = factura.residual
        residual_factura = factura.amount_total

        if factura.payment_ids:
            for p in factura.payment_ids:
                if p.state in ['posted']:
                    if p.payment_date > fecha_fin:
                        dias = (fecha_fin - factura.date_invoice)
                        # total_pagado += p.amount
                    else:
                        dias = (fecha_fin - factura.date_invoice)
                        r = 0
                        for linea in p.move_line_ids:
                            r += linea.debit

                        if r <= residual_factura:
                            residual_factura -= r
                        else:
                            residual_factura -= residual_factura
                # elif p.payment_date < fecha_fin:
                #     dias = (fecha_fin - factura.date_invoice)
            # total_pagado = factura.amount_total - total_pagado
                # else:
                #     if p.amount < factura.amount_total:
                #         dias = (fecha_fin - factura.date_invoice)
                #         total_pagado += factura.amount_total - p.amount
        else:
            dias = (fecha_fin - factura.date_invoice)
            residual_factura = factura.residual
        return {'dias':dias if dias == -1 else dias.days, 'saldo': residual_factura }


    def _get_facturas(self,fecha_inicio,fecha_fin):
        facturas = []
        totales = {'30': 0,'60': 0,'90': 0,'120': 0,'mas': 0,'total':0}
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['in_payment','open','paid'])])
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
                factura_datos = self.factura_pagada_fecha_fin(factura,datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date())
                dias = factura_datos['dias']
                saldo = factura_datos['saldo']
                # logging.warn(dias)
                if dias >=0:
                    if dias <= 30:
                        treinta = saldo
                    elif dias > 30 and dias <=60:
                        sesenta =  saldo
                    elif dias > 60 and dias <= 90:
                        noventa = saldo
                    elif dias > 90:
                        mas = saldo

                    f = {
                        'codigo': int(factura.partner_id.matricula),
                        'nombre': factura.partner_id.name,
                        'grado': factura.grado_id.nombre if factura.grado_id else '',
                        'numero': factura.name,
                        'fecha': factura.date_invoice,
                        '30': treinta,
                        '60': sesenta,
                        '90': noventa,
                        '120': ciento_veinte,
                        'mas': mas,
                        'saldo_factura': saldo
                    }

                    facturas.append(f)
        return facturas

    # def _get_facturas(self,fecha_inicio,fecha_fin):
    #     facturas = []
    #     facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['in_payment','open','paid'])],order="date_invoice asc")
    #
    #     if facturas_ids:
    #         fecha_hoy = date.today()
    #         for factura in facturas_ids:
    #             treinta = 0
    #             sesenta = 0
    #             noventa = 0
    #             ciento_veinte = 0
    #             mas = 0
    #             diferencia_dias = fecha_fin - factura.date_invoice
    #             dias = diferencia_dias.days
    #             if dias <= 30:
    #                 treinta = factura.residual
    #             elif dias > 30 and dias <=60:
    #                 sesenta =  factura.residual
    #             elif dias > 60 and dias <= 90:
    #                 noventa = factura.residual
    #             elif dias > 90 and dias <= 120:
    #                 ciento_veinte = factura.residual
    #             elif dias > 120:
    #                 mas = factura.residual
    #
    #
    #             f = {
    #                 'codigo': factura.partner_id.matricula,
    #                 'nombre': factura.partner_id.name,
    #                 'grado': factura.partner_id.grado_id.nombre if factura.partner_id.grado_id else '',
    #                 'numero': factura.number,
    #                 'fecha': factura.date_invoice,
    #                 '30': treinta,
    #                 '60': sesenta,
    #                 '90': noventa,
    #                 '120': ciento_veinte,
    #                 'mas': mas,
    #                 'saldo_factura': factura.residual
    #             }
    #             facturas.append(f)
    #     return facturas

    def generar_excel(self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Facturas')

            merge_format = libro.add_format({'align': 'center'})
            facturas = self._get_facturas(w.fecha_inicio,w.fecha_fin)
            # hoja.write(0, 0, 'Planilla')
            # hoja.write(0, 1, '')
            # hoja.write(0, 2, 'Periodo')
            # hoja.write(0, 3, w.fecha_inicio, formato_fecha)
            # hoja.write(0, 4, w.fecha_fin, formato_fecha)
            # #
            # #
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            titulo_bold = libro.add_format()
            titulo_bold.set_bold()
            columna_bold = libro.add_format()
            columna_bold.set_fg_color('#D7D7D7')
            columna_bold.set_bold()
            hoja.write(0,4,'ESCUELA BILINGÜE MAQUILISHUAT',titulo_bold)

            hoja.write(2,0,'Cliente',columna_bold)
            hoja.write(2,1,'Nombre',columna_bold)
            hoja.write(2,2,'Grado',columna_bold)
            hoja.write(2,3,'Número',columna_bold)
            hoja.write(2,4,'Fecha',columna_bold)
            hoja.write(2,5,'t0_30',columna_bold)
            hoja.write(2,6,'t31_60',columna_bold)
            hoja.write(2,7,'t61_90',columna_bold)
            hoja.write(2,8,'t91_120',columna_bold)
            hoja.write(2,9,'t121_mas',columna_bold)
            hoja.write(2,10,'saldo_factura',columna_bold)


            fila = 3
            if facturas:
                for factura in facturas:
                    hoja.write(fila,0,factura['codigo'])
                    hoja.write(fila,1,factura['nombre'])
                    hoja.write(fila,2,factura['grado'])
                    hoja.write(fila,3,factura['numero'])
                    hoja.write(fila,4,factura['fecha'],formato_fecha)
                    hoja.write(fila,5,factura['30'])
                    hoja.write(fila,6,factura['60'])
                    hoja.write(fila,7,factura['90'])
                    hoja.write(fila,8,factura['120'])
                    hoja.write(fila,9,factura['mas'])
                    hoja.write(fila,10,factura['saldo_factura'])

                    fila += 1

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'cuenta_por_cobrar.xls'})
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'maquilishuat.saldo_facturas.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_fin'])
        res = res and res[0] or {}
        datas['form'] = res
        logging.warn(datas)
        return self.env.ref('maquilishuat.action_saldo_facturas').report_action([], data=datas)
