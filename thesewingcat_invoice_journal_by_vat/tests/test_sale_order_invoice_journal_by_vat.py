from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestSaleOrderInvoiceJournalByVat(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.sale_journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company.id),
        ], limit=1)
        if not self.sale_journal:
            self.sale_journal = self.env['account.journal'].create({
                'name': 'Sales',
                'code': 'SAL',
                'type': 'sale',
                'company_id': self.company.id,
            })
        self.sale_journal_nif = self.env['account.journal'].create({
            'name': f'{self.sale_journal.name} NIF',
            'code': f'{(self.sale_journal.code or "SAL")}N',
            'type': 'sale',
            'company_id': self.company.id,
        })
        self.company.website_sale_invoice_journal_id = self.sale_journal
        self.company.website_sale_invoice_journal_nif_id = self.sale_journal_nif
        self.website = self.env['website'].search([], limit=1)
        self.partner = self.env['res.partner'].create({
            'name': 'E-commerce Test Partner',
            'email': 'test@example.com',
            'street': 'Street 1',
            'city': 'Madrid',
            'zip': '28001',
            'country_id': self.env.ref('base.es').id,
        })

    def _new_order(self, vat=False):
        partner = self.partner.copy({
            'vat': vat or False,
        })
        return self.env['sale.order'].new({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'website_id': self.website.id,
        })

    def test_prepare_invoice_uses_journal_without_vat(self):
        invoice_vals = self._new_order(vat=False)._prepare_invoice()
        self.assertEqual(invoice_vals['journal_id'], self.sale_journal.id)

    def test_prepare_invoice_uses_journal_with_vat(self):
        invoice_vals = self._new_order(vat='BE0123456789')._prepare_invoice()
        self.assertEqual(invoice_vals['journal_id'], self.sale_journal_nif.id)

