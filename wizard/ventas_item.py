# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import base64
import xlsxwriter
import io
import logging

class ventas_item_wizard(models.TransientModel):
    _name = 'maquilishuat.ventas_item.wizard'

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')


    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_fin'])
        res = res and res[0] or {}
        datas['form'] = res
        logging.warn(datas)
        return self.env.ref('maquilishuat.action_ventas_item').report_action([], data=datas)
