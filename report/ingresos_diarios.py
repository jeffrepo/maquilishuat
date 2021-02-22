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
                             if movimiento.ref:
                                 facturas = self.env["account.invoice"].search([('date_invoice','=', movimiento.date)])

                                 existe_factura = False
                                 for f in facturas:
                                     if f.number == movimiento.ref:
                                         existe_factura = True
                                         logging.warn('si igual')
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
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
