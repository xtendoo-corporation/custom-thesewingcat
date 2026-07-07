{
    "name": "Website Sale Invoice To Company",
    "summary": "Hace opcional u obligatorio el NIF y la empresa según un checkbox en checkout",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "author": "The Sewing Cat",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_es",
        "portal",
        "website_sale",
    ],
    "data": [
        "views/portal_address_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "thesewingcat_website_sale_invoice_to_company/static/src/interactions/address_invoice_to_company.js",
        ],
    },
    "installable": True,
}

