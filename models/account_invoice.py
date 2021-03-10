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

    @api.onchange('partner_id')
    def check_change(self):
        if self.partner_id:
            self.grado_rel_id = self.partner_id.grado_id
            self.ciclo_rel_id = self.partner_id.ciclo_id

class AccountInvoiceLinea(models.Model):
    _inherit = "account.invoice.line"

    mes_pagado = fields.Date('Mes pagado')
