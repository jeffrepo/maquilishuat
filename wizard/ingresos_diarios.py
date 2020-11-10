# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import base64
import xlsxwriter
import io
import logging
import xlrd
import base64

class ingresos_diarios_wizard(models.TransientModel):
    _name = 'maquilishuat.ingresos_diarios.wizard'

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    archivo = fields.Binary('Archivo excel')


    @api.multi
    def print_report_excel(self):
        workbook = xlrd.open_workbook(file_contents = base64.decodestring(self.archivo))
        sheet = workbook.sheet_by_index(0)
        #En ese ciclo se construye el diccionario con la informacion del archivo de excel.
        facturas = self.env['account.invoice'].search([])

        facturas_odoo = []
        for f in facturas:
            facturas_odoo.append(f.name)
        logging.warn(facturas_odoo)    
        for linea in range(sheet.nrows):
            if linea != 0:
                # fecha_excel = sheet.cell(linea, 10).value
                # fecha_excel = fecha_excel.replace("'", "")

                # fecha = datetime.datetime(*xlrd.xldate_as_tuple(fecha_excel, workbook.datemode))
                factura_excel = sheet.cell(linea, 3).value
                logging.warn(factura_excel)
                if factura_excel in facturas_odoo:
                    logging.warn('si existe')
                else:
                    logging.warn(factura_excel)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maquilishuat.ingresos_diarios.wizard',
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
        return self.env.ref('maquilishuat.action_ingresos_diarios').report_action([], data=datas)
