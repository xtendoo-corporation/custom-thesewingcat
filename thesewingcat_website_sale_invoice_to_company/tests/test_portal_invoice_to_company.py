import json
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.l10n_es.controllers.portal import L10nESPortalAccount as L10nESPortalAccountController
from odoo.addons.thesewingcat_website_sale_invoice_to_company.controllers.portal import (
    L10nESPortalAccount,
    WebsiteSale,
)
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSaleController
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon


@tagged('post_install', '-at_install')
class TestPortalInvoiceToCompany(WebsiteSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls._create_new_portal_user()

    def setUp(self):
        super().setUp()
        self.website_sale_controller = WebsiteSale()
        self.l10n_es_portal_controller = L10nESPortalAccount()
        self.default_billing_address_values = {
            'name': 'The Sewing Cat',
            'email': 'info@thesewingcat.test',
            'street': 'Calle Falsa 123',
            'city': 'Madrid',
            'zip': '28001',
            'country_id': self.country_be.id,
            'phone': '+34111111111',
            'address_type': 'billing',
        }

    def _parse_json_response(self, response):
        payload = response.get_data(as_text=True) if hasattr(response, 'get_data') else response
        return json.loads(payload)

    def _submit_address_as_user(self, user, sale_order, **values):
        website = self.website.with_user(user).with_context({})
        with MockRequest(website.env, website=website, sale_order_id=sale_order.id) as request:
            request.httprequest.method = 'POST'
            response = self.website_sale_controller.shop_address_submit(**values)
            return self._parse_json_response(response)

    def test_shop_address_submit_route_is_passthrough_to_standard_flow(self):
        website = self.website.with_user(self.public_user).with_context({})
        with MockRequest(website.env, website=website) as request, patch.object(
            WebsiteSaleController,
            'shop_address_submit',
            return_value=json.dumps({'redirectUrl': '/shop/checkout?try_skip_step=true'}),
        ) as mocked_submit:
            request.httprequest.method = 'POST'
            response = self.website_sale_controller.shop_address_submit(
                partner_id=-1,
                **self.default_billing_address_values,
                company_name='',
                vat='',
            )

        mocked_submit.assert_called_once()
        self.assertEqual(self._parse_json_response(response), {'redirectUrl': '/shop/checkout?try_skip_step=true'})

    def test_public_checkout_keeps_standard_checkout_redirect(self):
        sale_order = self._create_so(partner_id=self.website.user_id.partner_id.id)

        res = self._submit_address_as_user(
            self.public_user,
            sale_order,
            partner_id=-1,
            **self.default_billing_address_values,
            company_name='',
            vat='',
        )

        self.assertEqual(res, {'redirectUrl': '/shop/checkout?try_skip_step=true'})
        sale_order.invalidate_recordset()
        self.assertTrue(sale_order.partner_id)
        self.assertNotEqual(sale_order.partner_id, self.website.user_id.partner_id)
        self.assertTrue(sale_order.partner_invoice_id)
        self.assertTrue(sale_order.partner_shipping_id)
        self.assertFalse(sale_order.carrier_id)

    def test_company_name_and_vat_are_optional_when_checkbox_is_not_marked(self):
        sale_order = self._create_so(partner_id=self.portal_user.partner_id.id)

        res = self._submit_address_as_user(
            self.portal_user,
            sale_order,
            **self.default_billing_address_values,
            company_name='',
            vat='',
        )

        self.assertEqual(res, {'redirectUrl': '/shop/checkout?try_skip_step=true'})

    def test_invalid_vat_is_ignored_when_checkbox_is_not_marked(self):
        sale_order = self._create_so(partner_id=self.website.user_id.partner_id.id)

        res = self._submit_address_as_user(
            self.public_user,
            sale_order,
            partner_id=-1,
            **self.default_billing_address_values,
            company_name='',
            vat='INVALID VAT',
        )

        self.assertEqual(res, {'redirectUrl': '/shop/checkout?try_skip_step=true'})
        sale_order.invalidate_recordset()
        self.assertTrue(sale_order.partner_id)
        self.assertTrue(sale_order.partner_invoice_id)

    def test_not_marked_checkbox_never_returns_orphan_error_messages(self):
        website = self.website.with_user(self.public_user).with_context({})
        with MockRequest(website.env, website=website):
            invalid_fields, missing_fields, error_messages = self.website_sale_controller._validate_address_values(
                {
                    'name': 'The Sewing Cat',
                    'email': 'info@thesewingcat.test',
                    'phone': '+34111111111',
                    'street': 'Calle Falsa 123',
                    'city': 'Madrid',
                    'zip': '28001',
                    'country_id': self.country_be.id,
                    'company_name': '',
                    'vat': '',
                },
                self.env['res.partner'].sudo(),
                'billing',
                False,
                'name,email,vat,company_name',
            )

        self.assertEqual(invalid_fields, set())
        self.assertEqual(missing_fields, set())
        self.assertEqual(error_messages, [])

    def test_checkout_billing_address_check_does_not_require_vat(self):
        partner = self.env['res.partner'].sudo().create({
            'name': 'The Sewing Cat',
            'email': 'info@thesewingcat.test',
            'phone': '+34111111111',
            'street': 'Calle Falsa 123',
            'city': 'Madrid',
            'zip': '28001',
            'country_id': self.country_be.id,
        })
        website = self.website.with_user(self.public_user).with_context({})

        with MockRequest(website.env, website=website), patch.object(
            WebsiteSaleController,
            '_get_mandatory_billing_address_fields',
            return_value={'name', 'email', 'phone', 'street', 'city', 'zip', 'country_id', 'vat'},
        ):
            self.assertNotIn(
                'vat',
                self.l10n_es_portal_controller._get_mandatory_billing_address_fields(self.country_be),
            )
            self.assertTrue(self.l10n_es_portal_controller._check_billing_address(partner))

    def test_l10n_es_billing_address_check_does_not_require_vat(self):
        with patch.object(
            L10nESPortalAccountController,
            '_get_mandatory_billing_address_fields',
            return_value={'name', 'email', 'phone', 'street', 'city', 'zip', 'country_id', 'vat'},
        ):
            self.assertNotIn(
                'vat',
                self.l10n_es_portal_controller._get_mandatory_billing_address_fields(self.country_be),
            )

    def test_shop_checkout_does_not_redirect_to_address_when_only_vat_is_missing(self):
        partner = self.env['res.partner'].sudo().create({
            'name': 'The Sewing Cat',
            'email': 'info@thesewingcat.test',
            'phone': '+34111111111',
            'street': 'Calle Falsa 123',
            'city': 'Madrid',
            'zip': '28001',
            'country_id': self.country_be.id,
        })
        sale_order = self._create_so(
            partner_id=partner.id,
            partner_invoice_id=partner.id,
            partner_shipping_id=partner.id,
        )
        website = self.website.with_user(self.public_user).with_context({})

        with MockRequest(website.env, website=website, sale_order_id=sale_order.id) as request:
            request.httprequest.method = 'GET'
            response = self.website_sale_controller.shop_checkout(try_skip_step='true')

        self.assertFalse((getattr(response, 'location', None) or '').startswith('/shop/address'))

    def test_company_name_and_vat_are_required_when_checkbox_is_marked(self):
        sale_order = self._create_so(partner_id=self.portal_user.partner_id.id)

        res = self._submit_address_as_user(
            self.portal_user,
            sale_order,
            **self.default_billing_address_values,
            invoice_to_company='1',
            company_name='',
            vat='',
        )

        self.assertIn('company_name', res['invalid_fields'])
        self.assertIn('vat', res['invalid_fields'])
        self.assertIn('Para facturar a empresa, el nombre de la compañía y el NIF son obligatorios.', res['messages'])

    def test_company_name_and_vat_can_be_saved_when_checkbox_is_marked(self):
        sale_order = self._create_so(partner_id=self.portal_user.partner_id.id)

        res = self._submit_address_as_user(
            self.portal_user,
            sale_order,
            **self.default_billing_address_values,
            invoice_to_company='1',
            company_name='The Sewing Cat SL',
            vat='BE0926372368',
        )

        self.assertEqual(res, {'redirectUrl': '/shop/checkout?try_skip_step=true'})
        billing_address = self.portal_user.partner_id.child_ids.sorted('id', reverse=True)[0]
        self.assertEqual(billing_address.vat, 'BE0926372368')

