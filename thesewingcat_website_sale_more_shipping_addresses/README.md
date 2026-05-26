Website Sale More Shipping Addresses
====================================
Módulo mínimo para checkout y portal en Odoo.
Qué hace
--------
- Quita el botón de añadir dirección de facturación.
- Mantiene el alta de direcciones de entrega.
- Permite que esa alta de entrega aparezca también en checkout cuando el usuario es público.
- Mantiene la selección por tarjetas de las direcciones de entrega.
- Evita errores Javascript al alternar "misma que la dirección de entrega" sin botón de facturación.
Qué no hace
-----------
- No cambia la lógica de selección de direcciones en el pedido.
- No modifica ``/shop/update_address``.
- No cambia callbacks ni redirects estándar.
- No toca transportistas, pago ni confirmación.
Tests
-----
.. code-block:: bash
   docker compose run --rm odoo odoo -c /opt/odoo/auto/odoo.conf \
     -d test_more_shipping_addresses \
     --stop-after-init \
     -i thesewingcat_website_sale_more_shipping_addresses \
     --test-enable \
     --test-tags /thesewingcat_website_sale_more_shipping_addresses
