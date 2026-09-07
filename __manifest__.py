{
    "name": "JCDecaux - Purchase Order Report",
    "summary": "JCDecaux purchase order PDF layout",
    "version": "17.0.1.2.2",
    "category": "Purchases",
    "author": "JCDecaux",
    "license": "LGPL-3",
    "depends": ["purchase", "jcdecaux_purchase_approval"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/purchase_order_views.xml",
        "report/purchase_order_templates.xml",
        "report/purchase_order_report.xml",
        "data/report_action_data.xml",
        "data/mail_template_data.xml",
    ],
    "installable": True,
    "application": False,
}
