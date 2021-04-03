# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import base64
import xlsxwriter
import io
import logging

class producto_familia_wizard(models.TransientModel):
    _name = 'maquilishuat.producto_familia.wizard'

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    libros = fields.Boolean('Libros')
    uniformes = fields.Boolean('Uniformes')
    productos_ids = fields.Many2many('product.product',string='productos')

    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_fin','productos_ids'])
        res = res and res[0] or {}
        datas['form'] = res
        logging.warn(datas)
        return self.env.ref('maquilishuat.action_producto_familia').report_action([], data=datas)
