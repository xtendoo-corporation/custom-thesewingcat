Website Sale Invoice To Company
===============================

Módulo mínimo para Odoo website checkout.

Qué hace
--------

- Añade el checkbox Facturar a empresa en el formulario de dirección de checkout.
- Si el checkbox está marcado, company_name y vat son obligatorios.
- Si el checkbox no está marcado, company_name y vat no bloquean el envío del formulario.

Qué no hace
-----------

- No cambia el comportamiento de shop_address_submit.
- No cambia el comportamiento de shop_checkout.
- No cambia callbacks ni redirectUrl.
- No selecciona transportistas.
- No toca payment, delivery ni el flujo normal de Odoo.
- Las rutas de checkout se redeclaran solo como pass-through para asegurar el orden correcto de controladores.

El flujo esperado sigue siendo el estándar de Odoo, por ejemplo:

::

   POST /shop/address/submit -> 200
   GET /shop/checkout?try_skip_step=true -> 200
   POST /shop/get_delivery_rate -> 200

Tests
-----

::

   docker compose run --rm odoo odoo -c /opt/odoo/auto/odoo.conf \
     -d test_invoice_to_company \
     --stop-after-init \
     -i thesewingcat_website_sale_invoice_to_company \
     --test-enable \
     --test-tags /thesewingcat_website_sale_invoice_to_company

