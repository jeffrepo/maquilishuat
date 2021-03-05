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
import datetime
import time
import dateutil.parser


class ReportColegiaturasPagadasNo(models.AbstractModel):
    _name = 'report.maquilishuat.colegiaturas_pagadas_no'

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

    def colegiaturas_pagadas_nopagadas(self,fecha_inicio,fecha_fin):
        no_pagadas = {}
        pagadas = {}
        ciclo = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%Y'))
        mes = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%m'))
        mes_letras = self.mes_letras(fecha_fin)
        clientes_facturas = []
        partner_ids = self.env['account.invoice'].search([])
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=',fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['open','paid'])],order="date_invoice asc")
        facturas_pagadas_anteriormente = self.env['account.invoice'].search([('date_invoice','<',fecha_inicio),('type','=','out_invoice'),('state','in',['paid'])],order="date_invoice asc")
        if facturas_ids:
            for factura in facturas_ids:
                if factura.state == 'open':
                    # agregamos clientes para verificar despues si no tienen facturas en clientes_facturas
                    clientes_facturas.append(factura.partner_id.id)
                    for linea in factura.invoice_line_ids:
                        if 'Colegiaturas' in linea.name:
                            grado = factura.partner_id.grado_id
                            seccion = factura.partner_id.seccion_id
                            llave = str(grado.id)+'/'+str(seccion.id)
                            if llave not in no_pagadas:
                                no_pagadas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion': seccion.nombre,'subtotal':0}
                            no_pagadas[llave]['alumnos'].append({'matricula': factura.partner_id.matricula,'nombre': factura.partner_id.name, 'valor_pagado': 0})

                if factura.state == 'paid':
                    clientes_facturas.append(factura.partner_id.id)
                    for linea in factura.invoice_line_ids:
                        if 'Colegiaturas' in linea.name:
                            grado = factura.partner_id.grado_id
                            seccion = factura.partner_id.seccion_id
                            llave = str(grado.id)+'/'+str(seccion.id)
                            if llave not in pagadas:
                                pagadas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion':seccion.nombre,'subtotal':0,'cantidad': 0}
                            pagadas[llave]['alumnos'].append({'factura_no': factura.number,'matricula': factura.partner_id.matricula,'fecha': factura.date_invoice,'nombre': factura.partner_id.name, 'valor_pagado': linea.price_total})
                            pagadas[llave]['subtotal'] += linea.price_total
                            pagadas[llave]['cantidad'] += 1

        if facturas_pagadas_anteriormente:
            for factura in facturas_pagadas_anteriormente:
                for linea in factura.invoice_line_ids:
                    mes_f = False
                    grado = factura.partner_id.grado_id
                    seccion = factura.partner_id.seccion_id
                    llave = str(grado.id)+'/'+str(seccion.id)
                    if 'MENSUAL ANTICIPADO' in linea.name:
                        if ('enero' or 'Enero') in linea.name:
                            mes_f = 'ENERO'
                        if ('febrero' or 'feb' or 'Febrero') in linea.name:
                            mes_f = 'FEBRERO'
                        if ('marzo' or 'Marzo' or 'mzo') in linea.name:
                            mes_f = 'MARZO'
                        if ('abril' or 'Abril') in linea.name:
                            mes_f = 'ABRIL'
                        if ('mayo' or 'Mayo') in linea.name:
                            mes_f = 'MAYO'
                        if ('junio' or 'Junio') in linea.name:
                            mes_f = 'JUNIO'
                        if ('julio' or 'Julio') in linea.name:
                            mes_f = 'JUNIO'

                        if mes_f == mes_letras:
                            if llave not in pagadas:
                                pagadas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion':seccion.nombre ,'subtotal':0,'cantidad': 0}
                            pagadas[llave]['alumnos'].append({'factura_no': factura.number,'matricula': factura.partner_id.matricula,'fecha': factura.date_invoice,'nombre': factura.partner_id.name, 'valor_pagado': linea.price_total})
                            pagadas[llave]['subtotal'] += linea.price_total
                            pagadas[llave]['cantidad'] += 1


        if partner_ids:
            for cliente in partner_ids:
                if cliente.ciclo_id.nombre == ciclo and (cliente.id not in clientes_facturas):
                    grado = cliente.grado_id
                    seccion = cliente.seccion_id
                    llave = str(grado.id)+'/'+str(seccion.id)
                    if llave not in no_pagadas:
                        no_pagadas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion': seccion.nombre,'subtotal':0}
                    no_pagadas[llave]['alumnos'].append({'matricula': cliente.matricula,'nombre': cliente.name, 'valor_pagado': 0})


        logging.warn(pagadas)
        logging.warn(no_pagadas)
        return {'pagadas': pagadas.values() if pagadas else pagadas, 'no_pagadas': no_pagadas.values() if no_pagadas else no_pagadas}

    def facturas_nocreadas(self,fecha_inicio,fecha_fin):
        no_facturas = {}
        ciclo = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%Y'))
        mes = int(datetime.datetime.strptime(str(fecha_fin), '%Y-%m-%d').date().strftime('%m'))
        mes_letras = self.mes_letras(fecha_fin)
        clientes_facturas = []
        partner_ids = self.env['account.invoice'].search([])
        facturas_ids = self.env['account.invoice'].search([('date_invoice','>=',fecha_inicio),('date_invoice','<=',fecha_fin),('type','=','out_invoice'),('state','in',['open','paid'])],order="date_invoice asc")
        facturas_anteriores = self.env['account.invoice'].search([('date_invoice','<',fecha_inicio),('type','=','out_invoice'),('state','in',['open'])],order="date_invoice asc")
        if facturas_ids:
            for factura in facturas_ids:
                    # agregamos clientes para verificar despues si no tienen facturas en clientes_facturas
                clientes_facturas.append(factura.partner_id.id)
                    # for linea in factura.invoice_line_ids:
                    #     if 'Colegiaturas' in linea.name:
                    #         grado = factura.partner_id.grado_id
                    #         seccion = factura.partner_id.seccion_id
                    #         llave = str(grado.id)+'/'+str(seccion.id)
                    #         if llave not in no_facturas:
                    #             no_facturas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion': seccion.nombre,'subtotal':0,'cantidad': 0}
                    #         no_facturas[llave]['alumnos'].append({'matricula': factura.partner_id.matricula,'nombre': factura.partner_id.name, 'valor_pagado': 0})
                    #         no_facturas[llave]['cantidad'] += 1
                    #
        logging.warn(facturas_ids)            
        logging.warn(clientes_facturas)
        if partner_ids:
            for cliente in partner_ids:
                logging.warn(cliente.id)
                if (cliente.ciclo_id.nombre == ciclo) and (cliente.id not in clientes_facturas):
                # if cliente.ciclo_id.nombre == ciclo and (cliente.id not in clientes_facturas):
                    grado = cliente.grado_id
                    seccion = cliente.seccion_id
                    llave = str(grado.id)+'/'+str(seccion.id)
                    logging.warn('pasa')
                    if llave not in no_facturas:
                        no_facturas[llave] = {'grado': grado.nombre, 'alumnos': [],'seccion': seccion.nombre,'subtotal':0}
                    no_facturas[llave]['alumnos'].append({'matricula': cliente.matricula,'nombre': cliente.name, 'valor_pagado': 0})


        return no_facturas.values()

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
        facturadas = data.get('form', {}).get('facturadas', False)
        no_facturadas = data.get('form', {}).get('no_facturadas', False)
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
            'colegiaturas_pagadas_nopagadas': self.colegiaturas_pagadas_nopagadas,
            'facturadas': facturadas,
            'no_facturadas': no_facturadas,
            'facturas_nocreadas': self.facturas_nocreadas
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
