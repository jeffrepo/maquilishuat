# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import base64
import xlsxwriter
import io
import logging

class estado_cuenta_cliente_wizard(models.TransientModel):
    _name = 'maquilishuat.estado_cuenta_cliente.wizard'

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    cliente_id = fields.Many2one('res.partner','Cliente')

    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_fin','cliente_id'])
        res = res and res[0] or {}
        datas['form'] = res
        logging.warn(datas)
        return self.env.ref('maquilishuat.action_estado_cuenta_cliente').report_action([], data=datas)
