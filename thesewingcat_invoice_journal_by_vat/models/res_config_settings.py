from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_sale_invoice_journal_id = fields.Many2one(
        related='company_id.website_sale_invoice_journal_id',
        readonly=False,
    )
    website_sale_invoice_journal_nif_id = fields.Many2one(
        related='company_id.website_sale_invoice_journal_nif_id',
        readonly=False,
    )

