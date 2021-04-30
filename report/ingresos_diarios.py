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

    def _encabezado(self, fecha_inicio,fecha_fin):
        encabezado = 'ING'
        mes = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%m'))
        dia = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%d'))
        # movimientos = self.env["account.move.line"].search([("account_id","=", cuenta_id.id),("date","=",fecha_fin)],order="date asc")
        # primera_partida = movimientos[0]
        # dia = int(datetime.datetime.strptime(str(primera_partida.date), '%Y-%m-%d').date().strftime('%d'))

        encabezado += ' ' + str(mes) +'-'+str(dia)+'I'

        return encabezado

    def _get_facturas(self,fecha_inicio,fecha_fin):
        formas_pago = {}
        total_general = {'credito': 0, 'contado':0, 'total':0, 'cuota_mensual': 0,'otros_pagos':0,'pagos_anticipados':0}
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
        gravada = 0
        valor_neto = 0
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=', fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['open'])],order="date_invoice asc")
        total_general = {'credito': 0, 'contado':0, 'total':0, 'cuota_mensual': 0,'otros_pagos':0,'pagos_anticipados':0}
        pagos_ids = self.env['account.payment'].search([('payment_date','>=', fecha_inicio),('payment_date','<=',fecha_fin),('payment_type','=','inbound'),('state','in',['posted'])],order="payment_date asc")

        if facturas_ids:
            for factura in facturas_ids:
                if 'DAVIVIENDA Remesa' not in formas_pago:
                    formas_pago['DAVIVIENDA Remesa'] = {'forma_pago':'DAVIVIENDA Remesa', 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }
                formas_pago['DAVIVIENDA Remesa']['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': factura.amount_total,'contado': 0,'total': factura.amount_total,'cuota_mensual': 0,'otros_pagos':0,'pagos_anticipados':0})
                formas_pago['DAVIVIENDA Remesa']['subtotal']['credito'] += factura.amount_total
                formas_pago['DAVIVIENDA Remesa']['subtotal']['contado'] += 0
                formas_pago['DAVIVIENDA Remesa']['subtotal']['total'] += factura.amount_total
                formas_pago['DAVIVIENDA Remesa']['subtotal']['cuota_mensual'] += 0
                formas_pago['DAVIVIENDA Remesa']['subtotal']['pagos_anticipados'] += 0

                total_general['credito'] +=factura.amount_total
                total_general['contado'] +=0
                total_general['total'] +=factura.amount_total
                total_general['cuota_mensual'] +=0
                total_general['pagos_anticipados'] +=0

        for pago in pagos_ids:
            if pago.journal_id.default_debit_account_id.user_type_id.name == "Pasivos no-circulantes":
                if pago.journal_id.name not in formas_pago:
                    formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }
                formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': 0,'total': pago.amount,'cuota_mensual': 0,'otros_pagos':0,'pagos_anticipados': pago.amount})
                formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0
                formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0
                formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount
                formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += 0;
                formas_pago[pago.journal_id.name]['subtotal']['pagos_anticipados'] += pago.amount;

                total_general['credito'] +=pago.amount
                total_general['contado'] +=0
                total_general['total'] +=pago.amount
                total_general['cuota_mensual'] +=0
                total_general['pagos_anticipados'] +=pago.amount

                for linea in factura.invoice_line_ids:
                    if linea.product_id.type == "product":
                        gravada += linea.price_total
                        valor_neto += linea.price_subtotal

            else:

                for factura in pago.invoice_ids:

                    if factura.date_invoice < pago.payment_date:
                        logging.warn(factura.partner_id.name)
                        logging.warn('<')
                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }

                        formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': 0,'total': pago.amount,'cuota_mensual': 0,
                        'otros_pagos':pago.amount,'pagos_anticipados':0})

                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['otros_pagos'] += pago.amount
                        formas_pago[pago.journal_id.name]['subtotal']['pagos_anticipados'] += 0

                        total_general['credito'] +=0
                        total_general['contado'] +=0
                        total_general['total'] +=pago.amount
                        total_general['cuota_mensual'] +=0
                        total_general['otros_pagos'] +=pago.amount
                        total_general['pagos_anticipados'] +=0

                        for linea in factura.invoice_line_ids:
                            if linea.product_id.type == "product":
                                gravada += linea.price_total
                                valor_neto += linea.price_subtotal

                    if factura.date_invoice == pago.payment_date and factura.amount_total == pago.amount and factura.state in ['paid']:
                        logging.warn(factura.partner_id.name)
                        logging.warn('= fecha')

                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }

                        colegiatura = False
                        for linea in factura.invoice_line_ids:
                            if ('colegiaturas' or 'colegiatura') in linea.product_id.name.lower():
                                # formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount,
                                # 'otros_pagos':0,'pagos_anticipados':0})
                                colegiatura = True
                            # else:
                            #
                            #     formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': 0,
                            #     'otros_pagos':0,'pagos_anticipados':0})

                        if colegiatura:
                            formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount,
                            'otros_pagos':0,'pagos_anticipados':0})
                        else:
                            formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': 0,
                            'otros_pagos':0,'pagos_anticipados':0})

                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] += pago.amount
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount if colegiatura else 0
                        formas_pago[pago.journal_id.name]['subtotal']['otros_pagos'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['pagos_anticipados'] += 0

                        total_general['credito'] +=0
                        total_general['contado'] +=pago.amount
                        total_general['total'] +=pago.amount
                        total_general['cuota_mensual'] +=pago.amount if colegiatura else 0
                        total_general['otros_pagos'] +=0
                        total_general['pagos_anticipados'] +=0

                        for linea in factura.invoice_line_ids:
                            if linea.product_id.type == "product":
                                gravada += linea.price_total
                                valor_neto += linea.price_subtotal

                    if factura.date_invoice == pago.payment_date and factura.amount_total != pago.amount:
                        if pago.journal_id.name not in formas_pago:
                            formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }


                        colegiatura = False
                        for linea in factura.invoice_line_ids:
                            if ('colegiaturas' or 'colegiatura') in linea.product_id.name.lower():
                                # formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount,
                                # 'otros_pagos':0,'pagos_anticipados':0})
                                colegiatura = True

                        if colegiatura:
                            formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': factura.amount_total,'total': factura.amount_total,'cuota_mensual': factura.amount_total,
                            'otros_pagos':0,'pagos_anticipados':0})
                        else:
                            formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': factura.amount_total,'total': factura.amount_total,'cuota_mensual': 0,
                            'otros_pagos':0,'pagos_anticipados':0})

                        formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['contado'] += factura.amount_total
                        formas_pago[pago.journal_id.name]['subtotal']['total'] += factura.amount_total
                        formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += factura.amount_total if colegiatura else 0
                        formas_pago[pago.journal_id.name]['subtotal']['otros_pagos'] += 0
                        formas_pago[pago.journal_id.name]['subtotal']['pagos_anticipados'] += 0

                        total_general['credito'] +=0
                        total_general['contado'] +=factura.amount_total
                        total_general['total'] +=factura.amount_total
                        total_general['cuota_mensual'] +=factura.amount_total if colegiatura else 0
                        total_general['otros_pagos'] +=0
                        total_general['pagos_anticipados'] +=0

                        for linea in factura.invoice_line_ids:
                            if linea.product_id.type == "product":
                                gravada += linea.price_total
                                valor_neto += linea.price_subtotal

                    # ELIMINADO PERO PUEDE SERVIR
                    # if factura.date_invoice == pago.payment_date and factura.state in ['open']:
                    #     logging.warn(factura.partner_id.name)
                    #     logging.warn('= open')
                    #     if pago.journal_id.name not in formas_pago:
                    #         formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0,'otros_pagos':0,'pagos_anticipados':0 }  }
                    #
                    #     colegiatura = False
                    #     for linea in factura.invoice_line_ids:
                    #         if ('colegiaturas' or 'colegiatura') in linea.product_id.name.lower():
                    #             formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': factura.amount_total,'contado': 0,'total': pago.amount,'cuota_mensual': factura.amount_total,
                    #             'otros_pagos':0,'pagos_anticipados':0})
                    #             colegiatura = True
                    #         else:
                    #
                    #             formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': factura.amount_total,'contado': 0,'total': factura.amount_total,'cuota_mensual': 0,
                    #             'otros_pagos':0,'pagos_anticipados':0})
                    #
                    #     formas_pago[pago.journal_id.name]['subtotal']['credito'] += factura.amount_total
                    #     formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0
                    #     formas_pago[pago.journal_id.name]['subtotal']['total'] += factura.amount_total
                    #     formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += factura.amount_total if colegiatura else 0
                    #     formas_pago[pago.journal_id.name]['subtotal']['otros_pagos'] += 0
                    #     formas_pago[pago.journal_id.name]['subtotal']['pagos_anticipados'] += 0
                    #
                    #     total_general['credito'] +=factura.amount_total
                    #     total_general['contado'] +=0
                    #     total_general['total'] +=factura.amount_total
                    #     total_general['cuota_mensual'] +=factura.amount_total if factura.amount_total else 0
                    #     total_general['otros_pagos'] +=0
                    #     total_general['pagos_anticipados'] +=0
                    #
                    #     for linea in factura.invoice_line_ids:
                    #         if linea.product_id.type == "product":
                    #             gravada += linea.price_total
                    #             valor_neto += linea.price_subtotal
# --------------------------------------------------------


                    # elif factura.state == 'open':
                    #     if pago.journal_id.name not in formas_pago:
                    #         formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[] ,'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 }  }
                    #
                    #     formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': pago.amount,'contado': 0,'total': pago.amount,'cuota_mensual': pago.amount})
                    #     formas_pago[pago.journal_id.name]['subtotal']['credito'] += pago.amount
                    #     formas_pago[pago.journal_id.name]['subtotal']['contado'] += 0
                    #     formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount
                    #     formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;
                    #
                    #     total_general['credito'] +=pago.amount
                    #     total_general['contado'] +=0
                    #     total_general['total'] +=pago.amount
                    #     total_general['cuota_mensual'] +=pago.amount
                    #
                    # elif factura.state == 'paid':
                    #     for pago in factura.payment_ids:
                    #         if pago.journal_id.name not in formas_pago:
                    #             formas_pago[pago.journal_id.name] = {'forma_pago':pago.journal_id.name, 'facturas':[],'subtotal': {'credito':0,'contado':0,'total':0,'cuota_mensual':0 } }
                    #         formas_pago[pago.journal_id.name]['facturas'].append({'factura': factura.number,'fecha': factura.date_invoice, 'matricula': factura.partner_id.matricula,'nombre_cliente': factura.partner_id.name, 'credito': 0,'contado': pago.amount,'total': pago.amount,'cuota_mensual': pago.amount})
                    #         formas_pago[pago.journal_id.name]['subtotal']['credito'] += 0;
                    #         formas_pago[pago.journal_id.name]['subtotal']['contado'] +=  pago.amount;
                    #         formas_pago[pago.journal_id.name]['subtotal']['total'] += pago.amount;
                    #         formas_pago[pago.journal_id.name]['subtotal']['cuota_mensual'] += pago.amount;
                    #
                    #         total_general['credito'] += 0
                    #         total_general['contado'] += pago.amount
                    #         total_general['total'] +=pago.amount
                    #         total_general['cuota_mensual'] +=pago.amount
        logging.warn('PAGOS')
        logging.warn(total_general)
        return {'gravadas': gravada,'valor_neto':valor_neto,'formas_pago':formas_pago.values(),'total_general': total_general}

    # def _get_saldo_cuentas(self,fecha_fin,cuentas_ids):
    #     cuentas = []
    #     logging.warn('las cuentas')
    #     logging.warn(cuentas_ids)
    #     total ={'debe': 0, 'haber':0}
    #     if cuentas_ids:
    #         for cuenta in cuentas_ids:
    #             cuenta_id = self.env["account.account"].search([("id","=",cuenta)])
    #             movimientos = self.env["account.move.line"].search([("account_id","=", cuenta_id.id),("date","=",fecha_fin)])
    #             if movimientos:
    #                 if cuenta_id.user_type_id.name == 'Por cobrar':
    #
    #                     cuenta_dic = {
    #                         "codigo": cuenta_id.code,
    #                         "nombre": cuenta_id.name,
    #                         "movimientos": [],
    #                         "subtotal_debe": 0,
    #                         "subtotal_haber": 0,
    #                     }
    #                     for movimiento in movimientos:
    #                         if movimiento.ref:
    #                             logging.warn('si cobrar')
    #                             facturas = self.env["account.invoice"].search([('date_invoice','=', movimiento.date)])
    #                             logging.warn(facturas)
    #                             existe_factura = False
    #                             for f in facturas:
    #
    #                                 if f.reference == movimiento.ref:
    #                                     existe_factura = True
    #                                     logging.warn('si igual')
    #
    #                             if existe_factura == False:
    #                                 movimiento_dic = {
    #                                     "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
    #                                     "debe": 0,
    #                                     "haber": movimiento.credit,
    #                                 }
    #                                 cuenta_dic['subtotal_debe'] += 0
    #                                 cuenta_dic['subtotal_haber'] += movimiento.credit
    #                                 total['debe'] += 0
    #                                 total['haber'] += movimiento.credit
    #                                 cuenta_dic["movimientos"].append(movimiento_dic)
    #
    #                     if cuenta_dic['subtotal_debe'] > 0 or cuenta_dic['subtotal_haber'] > 0:
    #                         cuentas.append(cuenta_dic)
    #                 else:
    #                     cuenta_dic = {
    #                         "codigo": cuenta_id.code,
    #                         "nombre": cuenta_id.name,
    #                         "movimientos": [],
    #                         "subtotal_debe": 0,
    #                         "subtotal_haber": 0,
    #                     }
    #                     for movimiento in movimientos:
    #                         movimiento_dic = {
    #                             "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
    #                             "debe": movimiento.debit,
    #                             "haber": movimiento.credit,
    #                         }
    #                         cuenta_dic['subtotal_debe'] += movimiento.debit
    #                         cuenta_dic['subtotal_haber'] += movimiento.credit
    #                         total['debe'] += movimiento.debit
    #                         total['haber'] += movimiento.credit
    #                         cuenta_dic["movimientos"].append(movimiento_dic)
    #                     cuentas.append(cuenta_dic)
    #     logging.warn(cuentas)
    #     return {'cuentas':cuentas,'total': total}

    def _get_saldo_cuentas(self,fecha_fin,cuentas_ids):
        cuentas = []
        logging.warn('las cuentas')
        logging.warn(cuentas_ids)
        total ={'debe': 0, 'haber':0}
        if cuentas_ids:
            for cuenta in cuentas_ids:
                cuenta_id = self.env["account.account"].search([("id","=",cuenta)])
                movimientos = self.env["account.move.line"].search([("account_id","=", cuenta_id.id),("date","=",fecha_fin)])
                if movimientos:
                    if cuenta_id.user_type_id.name == 'Por cobrar':
                        cuenta_dic = {
                            "codigo": cuenta_id.code,
                             "nombre": cuenta_id.name,
                             "movimientos": [],
                             "subtotal_debe": 0,
                             "subtotal_haber": 0,
                              }
                        for movimiento in movimientos:
                             if movimiento.invoice_id and movimiento.invoice_id.date_invoice != movimiento.date:

                                 logging.warn('si tiene factura')
                                 movimiento_dic = {
                                    "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                    "debe": 0,
                                    "haber": movimiento.credit,
                                 }
                                 cuenta_dic['subtotal_debe'] += 0
                                 cuenta_dic['subtotal_haber'] += movimiento.credit
                                 total['debe'] += 0
                                 total['haber'] += movimiento.credit
                                 cuenta_dic["movimientos"].append(movimiento_dic)

                             if movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.date_invoice !=  movimiento.date:
                                 logging.warn('si tiene factura')
                                 movimiento_dic = {
                                     "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                     "debe": 0,
                                     "haber": movimiento.credit,
                                 }
                                 cuenta_dic['subtotal_debe'] += 0
                                 cuenta_dic['subtotal_haber'] += movimiento.credit
                                 total['debe'] += 0
                                 total['haber'] += movimiento.credit
                                 cuenta_dic["movimientos"].append(movimiento_dic)
                                 # if existe_factura == False:
                                 #     movimiento_dic = {
                                 #        "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                 #        "debe": 0,
                                 #        "haber": movimiento.credit,
                                 #     }
                                 #     cuenta_dic['subtotal_debe'] += 0
                                 #     cuenta_dic['subtotal_haber'] += movimiento.credit
                                 #     total['debe'] += 0
                                 #     total['haber'] += movimiento.credit
                                 #     cuenta_dic["movimientos"].append(movimiento_dic)

                        if cuenta_dic['subtotal_debe'] > 0 or cuenta_dic['subtotal_haber'] > 0:
                            cuentas.append(cuenta_dic)


                    else:
                        cuenta_dic = {
                            "codigo": cuenta_id.code,
                            "nombre": cuenta_id.name,
                            "movimientos": [],
                            "subtotal_debe": 0,
                            "subtotal_haber": 0,
                        }
                        for movimiento in movimientos:
                            movimiento_dic = {
                                "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                "debe": movimiento.debit,
                                "haber": movimiento.credit,
                            }
                            cuenta_dic['subtotal_debe'] += movimiento.debit
                            cuenta_dic['subtotal_haber'] += movimiento.credit
                            total['debe'] += movimiento.debit
                            total['haber'] += movimiento.credit
                            cuenta_dic["movimientos"].append(movimiento_dic)
                        cuentas.append(cuenta_dic)
        logging.warn(cuentas)
        return {'cuentas':cuentas,'total': total}


    def _get_reporte(self,fecha_fin,cuentas_ids):
        tipo_cuentas = [
            {

                        'nombre': 'Bancos locales',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_liquidity').id],
                        'codigo': '11010201',
                        'cuentas': [],
                        'type': 'efectivo_equivalente'
            },
            {

                        'nombre': 'Colegiaturas',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_receivable').id],
                        'codigo': '1103010101',
                        'cuentas': [],
                        'type': 'colegiaturas_debe'
            },
            {

                        'nombre': 'Gastos financieros',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_expenses').id],
                        'codigo': '4301',
                        'cuentas': [],
                        'type': 'gastos_financieros'
            },
            {

                        'nombre': 'Colegiaturas',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_receivable').id],
                        'codigo': '1103010101',
                        'cuentas': [],
                        'type': 'colegiaturas_haber'
            },
            {

                        'nombre': 'DOCUMENTOS POR PAGAR',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_current_liabilities').id],
                        'codigo': '210102',
                        'cuentas': [],
                        'type': 'documentos_por_pagar'
            },
            {

                        'nombre': 'RETENCIONES POR PAGAR EMPLEADOS',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_current_liabilities').id],
                        'codigo': '210104',
                        'cuentas': [],
                        'type': 'retencioes_pagar_empleados'
            },
            {

                        'nombre': 'DEBITO FISCAL',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_current_liabilities').id],
                        'codigo': '210402',
                        'cuentas': [],
                        'type': 'debito_fiscal'
            },
            {

                        'nombre': 'PERIODO 12-13',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_non_current_liabilities').id],
                        'codigo': '22060109',
                        'cuentas': [],
                        'type': 'periodo_12_13'
            },
            {

                        'nombre': 'INGRESOS POR SERVICIOS',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_revenue').id],
                        'codigo': '5101',
                        'cuentas': [],
                        'type': 'ingresos_servicios'
            },
            {
                        'nombre': 'INGRESOS NO OPERACIONALES',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_revenue').id],
                        'codigo': '5201',
                        'cuentas': [],
                        'type': 'ingresos_no_operacionales'

                        # 'nombre': 'INGRESOS NO OPERACIONALES',
                        # 'tipo_cuentas': [self.env.ref('account.data_account_type_other_income').id],
                        # 'codigo': '5202',
                        # 'cuentas': [],
                        # 'type': 'ingresos_no_operacionales'
            },
            {
                        'nombre': 'OTROS INGRESOS NO OPERACIONALES',
                        'tipo_cuentas': [self.env.ref('account.data_account_type_other_income').id],
                        'codigo': '5202',
                        'cuentas': [],
                        'type': 'otros_ingresos_no_operacionales'

                        # 'nombre': 'INGRESOS NO OPERACIONALES',
                        # 'tipo_cuentas': [self.env.ref('account.data_account_type_other_income').id],
                        # 'codigo': '5202',
                        # 'cuentas': [],
                        # 'type': 'ingresos_no_operacionales'
            },


        ]
        total_debe = 0
        total_haber = 0
        if cuentas_ids:
            for tipo in tipo_cuentas:
                for cuenta in cuentas_ids:
                    cuenta_id = self.env["account.account"].search([("id","=",cuenta)])
                    if cuenta_id.user_type_id.id in tipo['tipo_cuentas']:
                        cuenta_dic = {
                            'codigo': cuenta_id.code,
                            'nombre': cuenta_id.name,
                            'moves': [],
                            'debe': 0,
                            'haber': 0,
                            'subtotal_debe': 0,
                            'subtotal_haber': 0,
                        }


                        movimientos = self.env["account.move.line"].search([("account_id","=", cuenta_id.id),("date","=",fecha_fin)])
                        if movimientos:
                            if tipo['type'] in ['efectivo_equivalente','periodo_12_13']:
                                for movimiento in movimientos:
                                    if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['gastos_financieros'] and ('4301' in cuenta_id.code):
                                if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                    for movimiento in movimientos:
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['documentos_por_pagar'] and ('210102' in cuenta_id.code):
                                for movimiento in movimientos:
                                    if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['retencioes_pagar_empleados'] and ('210104' in cuenta_id.code):
                                for movimiento in movimientos:
                                    if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['debito_fiscal'] and ('210402' in cuenta_id.code):
                                for movimiento in movimientos:
                                    if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['ingresos_servicios'] and ('5101' in cuenta_id.code):
                                if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                    for movimiento in movimientos:
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' DEL '+str(movimiento.invoice_id.date_invoice)+' ' +str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['ingresos_no_operacionales'] and ('5201' in cuenta_id.code):
                                if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                    for movimiento in movimientos:
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' DEL '+str(movimiento.date)+' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['otros_ingresos_no_operacionales'] and ('5202' in cuenta_id.code):
                                for movimiento in movimientos:
                                    if (movimiento.payment_id and movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.type in ['out_invoice','out_refund']) or (movimiento.invoice_id and movimiento.invoice_id.type in ['out_invoice','out_refund']):
                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' DEL '+str(movimiento.date)+' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                            if tipo['type'] in ['colegiaturas_debe']:
                                for movimiento in movimientos:
                                    verificado_movimiento = False
                                    if movimiento.invoice_id:
                                        if movimiento.invoice_id.state == 'open':
                                            movimiento_dic = {
                                                "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                                "debe": movimiento.debit,
                                                "haber": movimiento.credit,
                                            }
                                            verificado_movimiento = True
                                            cuenta_dic['moves'].append(movimiento_dic)
                                            cuenta_dic['subtotal_debe'] += movimiento.debit
                                            cuenta_dic['subtotal_haber'] += movimiento.credit
                                        if movimiento.invoice_id.payment_ids and verificado_movimiento == False:
                                            pagado_fecha = True
                                            total_pagos = 0
                                            for p in movimiento.invoice_id.payment_ids:
                                                if p.payment_date != movimiento.invoice_id.date_invoice:
                                                    pagado_fecha = False
                                                else:
                                                    total_pagos += p.amount
                                            if pagado_fecha == False:
                                                movimiento_dic = {
                                                    "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                                    "debe": movimiento.debit,
                                                    "haber": movimiento.credit,
                                                }
                                                cuenta_dic['moves'].append(movimiento_dic)
                                                cuenta_dic['subtotal_debe'] += movimiento.debit
                                                cuenta_dic['subtotal_haber'] += movimiento.credit

                                            if total_pagos == movimiento.invoice_id.amount_total and movimiento.invoice_id.credito:
                                                movimiento_dic = {
                                                    "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                                    "debe": movimiento.debit,
                                                    "haber": movimiento.credit,
                                                }
                                                cuenta_dic['moves'].append(movimiento_dic)
                                                cuenta_dic['subtotal_debe'] += movimiento.debit
                                                cuenta_dic['subtotal_haber'] += movimiento.credit

                            if tipo['type'] in ['colegiaturas_haber']:
                                for movimiento in movimientos:
                                    # if movimiento.payment_id and ((movimiento.payment_id.payment_date != movimiento.payment_id.invoice_ids.date_invoice) or (movimiento.payment_id.payment_date == movimiento.payment_id.invoice_ids.date_invoice and movimiento.credit < movimiento.payment_id.invoice_ids.amount_total)):
                                    if movimiento.payment_id and ((movimiento.payment_id.payment_date != movimiento.payment_id.invoice_ids.date_invoice)):

                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' DE '+str(movimiento.payment_id.invoice_ids.date_invoice)+' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit

                                    # variable validacion es para que no agregue el movimiento 2 veces
                                    validacion1 = False
                                    if movimiento.payment_id and ((movimiento.payment_id.payment_date == movimiento.payment_id.invoice_ids.date_invoice and movimiento.payment_id.invoice_ids.credito)):

                                        movimiento_dic = {
                                            "concepto": str(movimiento.ref)+ ' DE '+str(movimiento.payment_id.invoice_ids.date_invoice)+' ' + str(movimiento.partner_id.name),
                                            "debe": movimiento.debit,
                                            "haber": movimiento.credit,
                                        }
                                        cuenta_dic['moves'].append(movimiento_dic)
                                        cuenta_dic['subtotal_debe'] += movimiento.debit
                                        cuenta_dic['subtotal_haber'] += movimiento.credit
                                        validacion1 = True

                                    if movimiento.payment_id:
                                        if movimiento.payment_id.invoice_ids and movimiento.payment_id.invoice_ids.credito and validacion1==False:
                                            total_pagos = 0
                                            for pago in movimiento.payment_id.invoice_ids.payment_ids:
                                                if pago.payment_date == movimiento.payment_id.invoice_ids.date_invoice:
                                                    total_pagos += pago.amount

                                            if total_pagos == movimiento.payment_id.invoice_ids.amount_total:
                                                movimiento_dic = {
                                                    "concepto": str(movimiento.ref)+ ' DE '+str(movimiento.payment_id.invoice_ids.date_invoice)+' ' + str(movimiento.partner_id.name),
                                                    "debe": movimiento.debit,
                                                    "haber": movimiento.credit,
                                                }
                                                cuenta_dic['moves'].append(movimiento_dic)
                                                cuenta_dic['subtotal_debe'] += movimiento.debit
                                                cuenta_dic['subtotal_haber'] += movimiento.credit


                            total_debe += cuenta_dic['subtotal_debe']
                            total_haber += cuenta_dic['subtotal_haber']
                                    # if movimiento.payment_id and movimiento.payment_id.invoice_ids:
                                    #     pagado_fecha = True
                                    #     for p in movimiento.payment_id.invoice_ids.payment_ids:
                                    #         if p.payment_date != movimiento.payment_id.invoice_ids.date_invoice:
                                    #             pagado_fecha = False
                                    #     if pagado_fecha == False:
                                    #         movimiento_dic = {
                                    #             "concepto": str(movimiento.ref)+ ' ' + str(movimiento.partner_id.name),
                                    #             "debe": movimiento.debit,
                                    #             "haber": movimiento.credit,
                                    #         }
                                    #         cuenta_dic['moves'].append(movimiento_dic)
                                    #         cuenta_dic['subtotal_debe'] += movimiento.debit
                                    #         cuenta_dic['subtotal_haber'] += movimiento.credit
                        if cuenta_dic['moves']:
                            tipo['cuentas'].append(cuenta_dic)
        logging.warn(tipo_cuentas)

        return [tipo_cuentas,total_debe,total_haber]

    def fecha_actual(self):
        # logging.warn(datetime.datetime.now())

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hora = datetime.datetime.now().astimezone(timezone).strftime('%d/%m/%Y')
        # logging.warn(fecha_hora)
        return fecha_hora

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = 'account.invoice'
        fecha_fin = data.get('form', {}).get('fecha_fin', False)
        fecha_inicio = data.get('form', {}).get('fecha_inicio', False)
        cuentas_ids = data.get('form', {}).get('cuentas_ids', False)
        correlativo = data.get('form', {}).get('correlativo', False)
        # formato_planilla_id = data.get('form', {}).get('formato_planilla_id', False)
        docs = self.env[self.model].browse(docids)
        logging.warn(docs)


        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'fecha_fin': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'cuentas_ids': cuentas_ids,
            '_get_facturas': self._get_facturas,
            '_get_pagos': self._get_pagos,
            'fecha_actual': self.fecha_actual,
            '_get_saldo_cuentas': self._get_saldo_cuentas,
            '_get_reporte': self._get_reporte,
            '_encabezado': self._encabezado,
            'correlativo': correlativo,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
