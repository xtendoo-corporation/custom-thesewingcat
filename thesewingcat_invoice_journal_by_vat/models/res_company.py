from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    website_sale_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Website Sale Invoice Journal',
        domain="[('type', '=', 'sale'), ('company_id', '=', id)]",
        check_company=True,
        help='Journal used for e-commerce invoices when the customer has no VAT/NIF.',
    )
    website_sale_invoice_journal_nif_id = fields.Many2one(
        'account.journal',
        string='Website Sale Invoice Journal with NIF',
        domain="[('type', '=', 'sale'), ('company_id', '=', id)]",
        check_company=True,
        help='Journal used for e-commerce invoices when the customer has a VAT/NIF.',
    )

