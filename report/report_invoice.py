# -*- coding: utf-8 -*-

from odoo import api, models
import re
import odoo.addons.l10n_gt_extra.a_letras

class ReportAbstractInvoice(models.AbstractModel):
    _name = 'maquilishuat.abstract.reporte_account_invoice'

    nombre_reporte = ''


    @api.model
    def get_report_values(self, docids, data=None):
        self.model = 'account.invoice'
        docs = self.env[self.model].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
        }

class ReportInvoice1(models.AbstractModel):
    _name = 'report.buenrollo.reporte_account_invoice1'
    _inherit = 'maquilishuat.abstract.reporte_account_invoice'

    nombre_reporte = 'buenrollo.reporte_account_invoice1'
