from odoo import api, models
from odoo.http import request
from odoo.tools import str2bool


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        httprequest = getattr(request, 'httprequest', None)
        if httprequest and httprequest.path in {'/shop/address/submit', '/my/address/submit'}:
            invoice_to_company = str2bool(
                request.params.get('invoice_to_company')
                or httprequest.form.get('invoice_to_company')
                or 'false'
            )
            if invoice_to_company:
                for vals in vals_list:
                    vals['is_company'] = False
                    vals['company_type'] = 'person'
        return super().create(vals_list)

