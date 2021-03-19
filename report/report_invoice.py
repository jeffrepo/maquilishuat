# -*- coding: utf-8 -*-

from odoo import api, models
import re

class ReportAbstractInvoice(models.AbstractModel):
    _name = 'maquilishuat.abstract.reporte_account_invoice'

    nombre_reporte = ''


    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = 'account.invoice'
        docs = self.env[self.model].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
        }

class ReportInvoice1(models.AbstractModel):
    _name = 'report.maquilishuat.reporte_account_invoice1'
    _inherit = 'maquilishuat.abstract.reporte_account_invoice'

    nombre_reporte = 'maquilishuat.reporte_account_invoice1'
