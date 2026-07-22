from odoo import models

from ..constants import DEFAULT_GENERAL_TERMS, GENERAL_TERMS_PARAM


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _jcdecaux_supplier_code(self):
        """Return the standard supplier reference until the SAP field is known."""
        self.ensure_one()
        partner = self.partner_id
        return partner.ref or partner.commercial_partner_id.ref or ""

    def _jcdecaux_delivery_partner(self):
        """Resolve the most specific standard delivery address available."""
        self.ensure_one()
        if "dest_address_id" in self._fields and self.dest_address_id:
            return self.dest_address_id

        # purchase_stock adds picking_type_id. Keep this module installable with
        # purchase alone while using the warehouse address when it is available.
        if "picking_type_id" in self._fields and self.picking_type_id:
            warehouse = self.picking_type_id.warehouse_id
            warehouse_partner = getattr(warehouse, "partner_id", False)
            if warehouse_partner:
                return warehouse_partner

        return self.company_id.partner_id

    def _jcdecaux_observation_lines(self):
        self.ensure_one()
        return self.order_line.filtered(lambda line: line.display_type == "line_note")

    def _jcdecaux_general_terms(self):
        self.ensure_one()
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(GENERAL_TERMS_PARAM, DEFAULT_GENERAL_TERMS)
        )

    def _jcdecaux_exchange_rate(self):
        """Use Odoo's stored PO conversion rate and retain the requested fallback."""
        self.ensure_one()
        return self.currency_rate or 1.0
