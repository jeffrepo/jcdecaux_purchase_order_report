{
    "name": "JCDecaux - Purchase Order Report",
    "summary": "JCDecaux purchase order PDF layout",
    "version": "17.0.1.1.0",
    "category": "Purchases",
    "author": "JCDecaux",
    "license": "LGPL-3",
    "depends": ["purchase", "jcdecaux_purchase_approval"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/purchase_order_views.xml",
        "report/purchase_order_templates.xml",
        "report/purchase_order_report.xml",
    ],
    "installable": True,
    "application": False,
}
