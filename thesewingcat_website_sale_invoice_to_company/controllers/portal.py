from odoo.addons.l10n_es.controllers.portal import L10nESPortalAccount as L10nESPortalAccountController
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSaleController
from odoo.http import route
from odoo.tools import str2bool
from odoo.tools.translate import _


class L10nESPortalAccount(L10nESPortalAccountController):

    def _get_mandatory_billing_address_fields(self, country_sudo):
        field_names = super()._get_mandatory_billing_address_fields(country_sudo)
        field_names.discard('vat')
        return field_names


class WebsiteSale(WebsiteSaleController):

    @staticmethod
    def _is_invoice_to_company_enabled(value):
        if isinstance(value, bool):
            return value
        return str2bool(value or 'false')

    def _prepare_address_form_values(
        self, partner_sudo, address_type='billing', use_delivery_as_billing=False, callback='', **kwargs
    ):
        values = super()._prepare_address_form_values(
            partner_sudo,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **kwargs,
        )
        values['invoice_to_company'] = self._is_invoice_to_company_enabled(
            kwargs.get('invoice_to_company')
        )
        return values

    @route(
        '/shop/checkout', type='http', methods=['GET'], auth='public', website=True,
        sitemap=False,
    )
    def shop_checkout(self, try_skip_step=None, **query_params):
        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)

    @route(
        '/shop/address/submit', type='http', methods=['POST'], auth='public', website=True,
        sitemap=False,
    )
    def shop_address_submit(
        self,
        partner_id=None,
        address_type='billing',
        use_delivery_as_billing=None,
        callback=None,
        **form_data,
    ):
        return super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **form_data,
        )

    def _complete_address_values(
        self, address_values, address_type, use_delivery_as_billing, **kwargs
    ):
        super()._complete_address_values(
            address_values,
            address_type,
            use_delivery_as_billing,
            **kwargs,
        )
        if self._is_invoice_to_company_enabled(kwargs.get('invoice_to_company')):
            address_values['is_company'] = False

    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        **kwargs,
    ):
        invoice_to_company = self._is_invoice_to_company_enabled(kwargs.get('invoice_to_company'))
        invoice_company_fields = {'company_name', 'vat'}

        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            **kwargs,
        )
        company_required_message = _(
            "Para facturar a empresa, el nombre de la compañía y el NIF son obligatorios."
        )

        if not invoice_to_company:
            missing_fields -= invoice_company_fields
            invalid_fields -= invoice_company_fields
            if not invalid_fields and not missing_fields:
                error_messages = []
            return invalid_fields, missing_fields, error_messages

        if address_type == 'billing' or use_delivery_as_billing:
            for field_name in invoice_company_fields:
                if not address_values.get(field_name):
                    missing_fields.add(field_name)
            if invoice_company_fields & missing_fields and company_required_message not in error_messages:
                error_messages.append(company_required_message)

        return invalid_fields, missing_fields, error_messages

