from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        values = super()._prepare_invoice()
        if self.website_id:
            has_vat = bool((self.partner_invoice_id.vat or '').strip())
            company = self.company_id
            journal = (
                company.website_sale_invoice_journal_nif_id
                if has_vat
                else company.website_sale_invoice_journal_id
            )
            if journal:
                values['journal_id'] = journal.id
        return values

