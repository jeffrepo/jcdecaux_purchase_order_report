from odoo import fields, models

from ..constants import DEFAULT_GENERAL_TERMS, GENERAL_TERMS_PARAM


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    jcdecaux_purchase_general_terms = fields.Text(
        string="Condiciones generales de la orden de compra JCDecaux",
        config_parameter=GENERAL_TERMS_PARAM,
        default=DEFAULT_GENERAL_TERMS,
        groups="base.group_system",
    )
