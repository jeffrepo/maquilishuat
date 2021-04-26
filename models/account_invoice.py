# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    grado_rel_id = fields.Many2one('colegio.grado','Grado', store=True)
    ciclo_rel_id = fields.Many2one('colegio.ciclo','Ciclo', store=True)
    matricula_rel = fields.Char('Matricula', related="partner_id.matricula",store=True)
    credito = fields.Boolean('Credito')
    tipo_factura_compra = fields.Selection([ ('credito_fiscal', 'Credito fiscal'),('factura', 'factura')],'Tipo factura compra')


    @api.onchange('partner_id')
    def check_change(self):
        if self.partner_id:
            self.grado_rel_id = self.partner_id.grado_id
            self.ciclo_rel_id = self.partner_id.ciclo_id

class AccountInvoiceLinea(models.Model):
    _inherit = "account.invoice.line"

    mes_pagado = fields.Date('Mes pagado')
    precio_sin_impuesto = fields.Float('Precio sin impuesto')


    @api.onchange('precio_sin_impuesto')
    def _onchange_precio_sin_impuesto(self):
        res = {}
        if self.precio_sin_impuesto > 0:
            self.price_unit = (self.precio_sin_impuesto * 1.13)
        return res

class ResPartner(models.Model):
    _inherit = "res.partner"

    nrc = fields.Char('Numero de registro de contribuyente')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    colegiaturas = fields.Boolean('Colegiaturas')
    inscripciones = fields.Boolean('inscripciones')
    varios = fields.Boolean('Varias')

# class AccountJournal(models.Model):
#     _inherit = "account.journal"
#
#     tipo_factura_compra = fields.Selection([ ('credito_fiscal', 'Credito fiscal'),('factura', 'factura')],'Tipo factura compra')
