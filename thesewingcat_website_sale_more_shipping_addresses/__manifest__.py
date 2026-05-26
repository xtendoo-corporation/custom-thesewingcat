{
    "name": "Website Sale More Shipping Addresses",
    "summary": "Quita el alta de facturación y permite añadir más direcciones de entrega",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "author": "The Sewing Cat",
    "license": "AGPL-3",
    "depends": [
        "portal",
        "website_sale",
    ],
    "data": [
        "views/address_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "thesewingcat_website_sale_more_shipping_addresses/static/src/interactions/address_card_more_shipping_addresses.js",
            "thesewingcat_website_sale_more_shipping_addresses/static/src/interactions/checkout_more_shipping_addresses.js",
        ],
    },
    "installable": True,
}
