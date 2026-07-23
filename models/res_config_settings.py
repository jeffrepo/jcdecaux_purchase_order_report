from odoo import api, fields, models

from ..constants import DEFAULT_GENERAL_TERMS, GENERAL_TERMS_PARAM


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    jcdecaux_purchase_general_terms = fields.Text(
        string="Condiciones generales de la orden de compra JCDecaux",
        default=DEFAULT_GENERAL_TERMS,
        groups="base.group_system",
    )

    @api.model
    def get_values(self):
        values = super().get_values()
        values["jcdecaux_purchase_general_terms"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(GENERAL_TERMS_PARAM, DEFAULT_GENERAL_TERMS)
        )
        return values

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            GENERAL_TERMS_PARAM,
            self.jcdecaux_purchase_general_terms or "",
        )
