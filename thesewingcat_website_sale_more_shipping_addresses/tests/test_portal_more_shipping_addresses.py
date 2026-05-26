import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSaleController
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon
from odoo.tests import tagged
@tagged('post_install', '-at_install')
class TestPortalMoreShippingAddresses(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls._create_new_portal_user()
    def setUp(self):
        super().setUp()
        self.website_sale_controller = WebsiteSaleController()
        self.portal_controller = CustomerPortal()
        self.delivery_address_values = {
            'name': 'Entrega Test',
            'email': 'entrega@thesewingcat.test',
            'street': 'Calle Entrega 42',
            'city': 'Huelva',
            'zip': '21001',
            'country_id': self.country_be.id,
            'phone': '+34123456789',
            'address_type': 'delivery',
        }
    def _parse_json_response(self, response):
        payload = response.get_data(as_text=True) if hasattr(response, 'get_data') else response
        return json.loads(payload)
    def _render_template(self, xmlid, values):
        return str(self.env['ir.ui.view']._render_template(xmlid, values))
    def test_checkout_shows_delivery_add_button_for_public_user_and_hides_billing_one(self):
        partner = self.env['res.partner'].sudo().create({
            'name': 'Checkout Partner',
            'email': 'checkout@thesewingcat.test',
            'phone': '+34999999999',
            'street': 'Calle Principal 1',
            'city': 'Sevilla',
            'zip': '41001',
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
            render_values = self.website_sale_controller._prepare_checkout_page_values(sale_order)
            delivery_html = self._render_template('website_sale.delivery_address_list', render_values)
            billing_html = self._render_template('website_sale.billing_address_list', render_values)
        self.assertIn('data-address-type="delivery"', delivery_html)
        self.assertIn('o_address_card_add_new btn btn-outline-primary btn-sm', delivery_html)
        self.assertNotIn('o_add_billing_address_btn', billing_html)
    def test_checkout_public_user_can_create_another_delivery_address_for_existing_partner(self):
        partner = self.env['res.partner'].sudo().create({
            'name': 'Checkout Partner',
            'email': 'checkout@thesewingcat.test',
            'phone': '+34999999999',
            'street': 'Calle Principal 1',
            'city': 'Sevilla',
            'zip': '41001',
            'country_id': self.country_be.id,
        })
        existing_delivery = self.env['res.partner'].sudo().create({
            'parent_id': partner.id,
            'type': 'delivery',
            'name': 'Entrega Inicial',
            'email': 'inicial@thesewingcat.test',
            'phone': '+34000000001',
            'street': 'Calle Inicial 1',
            'city': 'Sevilla',
            'zip': '41002',
            'country_id': self.country_be.id,
        })
        sale_order = self._create_so(
            partner_id=partner.id,
            partner_invoice_id=partner.id,
            partner_shipping_id=existing_delivery.id,
        )
        website = self.website.with_user(self.public_user).with_context({})
        with MockRequest(website.env, website=website, sale_order_id=sale_order.id) as request:
            request.httprequest.method = 'POST'
            response = self.website_sale_controller.shop_address_submit(
                **self.delivery_address_values,
            )
        payload = self._parse_json_response(response)
        self.assertEqual(payload, {'redirectUrl': '/shop/checkout?try_skip_step=true'})
        sale_order.invalidate_recordset()
        self.assertEqual(sale_order.partner_shipping_id.type, 'delivery')
        self.assertEqual(sale_order.partner_shipping_id.parent_id, partner)
        self.assertEqual(len(partner.child_ids.filtered(lambda p: p.type == 'delivery')), 2)
    def test_portal_addresses_hide_billing_add_button_and_keep_delivery_one(self):
        combined_arch = self.env.ref('portal.my_addresses').get_combined_arch()
        self.assertIn('o_address_card_add_new btn btn-outline-primary btn-sm', combined_arch)
        self.assertNotIn('o_add_billing_address_btn', combined_arch)
