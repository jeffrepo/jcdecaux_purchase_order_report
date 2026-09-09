import base64
import io

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.pdf import PdfFileReader, PdfFileWriter


class TestPurchaseOrderReport(TransactionCase):
    @staticmethod
    def _make_pdf(page_count=1):
        writer = PdfFileWriter()
        for _page in range(page_count):
            writer.addBlankPage(width=612, height=792)
        stream = io.BytesIO()
        writer.write(stream)
        return stream.getvalue()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Proveedor de prueba",
                "ref": "SAP-5000034800",
                "supplier_rank": 1,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Acrílico 12x30",
                "default_code": "PROD0001",
                "purchase_ok": True,
            }
        )
        cls.payment_term = cls.env["account.payment.term"].create(
            {"name": "45 días"}
        )
        cls.purchase_tax = cls.env["account.tax"].create(
            {
                "name": "IVA compras 15%",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "company_id": cls.env.company.id,
            }
        )
        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "payment_term_id": cls.payment_term.id,
                "currency_id": cls.env.company.currency_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": "PROD0001 Acrílico 12x30",
                            "product_qty": 2.0,
                            "product_uom": cls.product.uom_po_id.id,
                            "price_unit": 125.0,
                            "taxes_id": [Command.set(cls.purchase_tax.ids)],
                            "date_planned": fields.Datetime.now(),
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_note",
                            "name": "Prueba de notas en línea",
                        }
                    ),
                ],
            }
        )

    def test_report_uses_odoo_computed_amounts(self):
        product_line = self.order.order_line.filtered(
            lambda line: not line.display_type
        )

        self.assertAlmostEqual(product_line.price_subtotal, 250.0, places=2)
        self.assertAlmostEqual(product_line.price_tax, 37.5, places=2)
        self.assertAlmostEqual(product_line.price_total, 287.5, places=2)
        self.assertAlmostEqual(self.order.amount_untaxed, 250.0, places=2)
        self.assertAlmostEqual(self.order.amount_tax, 37.5, places=2)
        self.assertAlmostEqual(self.order.amount_total, 287.5, places=2)

    def test_report_helpers(self):
        self.assertEqual(self.order._jcdecaux_supplier_code(), "SAP-5000034800")
        self.assertEqual(
            self.order._jcdecaux_observation_lines().mapped("name"),
            ["Prueba de notas en línea"],
        )
        self.assertEqual(self.order._jcdecaux_exchange_rate(), 1.0)

        self.env["ir.config_parameter"].sudo().set_param(
            "jcdecaux_purchase_order_report.general_terms",
            "Condiciones configuradas para la prueba.",
        )
        self.assertEqual(
            self.order._jcdecaux_general_terms(),
            "Condiciones configuradas para la prueba.",
        )

    def test_multiline_general_terms_settings_are_loaded_and_saved(self):
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param(
            "jcdecaux_purchase_order_report.general_terms",
            "Primera línea.\nSegunda línea.",
        )

        defaults = self.env["res.config.settings"].default_get(
            ["jcdecaux_purchase_general_terms"]
        )

        self.assertEqual(
            defaults["jcdecaux_purchase_general_terms"],
            "Primera línea.\nSegunda línea.",
        )

        settings = self.env["res.config.settings"].create(
            {
                "jcdecaux_purchase_general_terms": (
                    "Condiciones actualizadas.\nCon texto multilínea."
                )
            }
        )
        settings.set_values()
        self.assertEqual(
            parameters.get_param(
                "jcdecaux_purchase_order_report.general_terms"
            ),
            "Condiciones actualizadas.\nCon texto multilínea.",
        )

    def test_purchase_appendix_is_available_in_company_settings(self):
        appendix_pdf = self._make_pdf(page_count=2)
        self.env.company.write(
            {
                "jcdecaux_purchase_appendix_pdf": base64.b64encode(
                    appendix_pdf
                ),
                "jcdecaux_purchase_appendix_filename": "condiciones.pdf",
            }
        )

        settings = self.env["res.config.settings"].create(
            {"company_id": self.env.company.id}
        )

        self.assertEqual(
            base64.b64decode(settings.jcdecaux_purchase_appendix_pdf),
            appendix_pdf,
        )
        self.assertEqual(
            settings.jcdecaux_purchase_appendix_filename,
            "condiciones.pdf",
        )

    def test_purchase_appendix_rejects_invalid_pdf(self):
        with self.assertRaises(ValidationError):
            self.env.company.jcdecaux_purchase_appendix_pdf = (
                base64.b64encode(b"This is not a PDF")
            )

    def test_purchase_appendix_is_merged_after_report(self):
        purchase_pdf = self._make_pdf()
        appendix_pdf = self._make_pdf(page_count=2)
        self.env.company.write(
            {
                "jcdecaux_purchase_appendix_pdf": base64.b64encode(
                    appendix_pdf
                ),
                "jcdecaux_purchase_appendix_filename": "condiciones.pdf",
            }
        )
        report = self.env.ref(
            "jcdecaux_purchase_order_report.action_report_purchase_order_jcdecaux"
        )
        streams = {
            self.order.id: {
                "stream": io.BytesIO(purchase_pdf),
                "attachment": None,
            }
        }

        result = self.env["ir.actions.report"]._jcdecaux_append_purchase_pdf(
            streams,
            report,
            self.order.ids,
        )

        merged_pdf = result[self.order.id]["stream"].getvalue()
        reader = PdfFileReader(io.BytesIO(merged_pdf), strict=False)
        self.assertEqual(reader.numPages, 3)

    def test_delivery_address_prefers_purchase_destination(self):
        if "dest_address_id" not in self.order._fields:
            self.assertEqual(
                self.order._jcdecaux_delivery_partner(),
                self.env.company.partner_id,
            )
            return

        delivery_partner = self.env["res.partner"].create(
            {
                "name": "Bodega de entrega",
                "parent_id": self.vendor.id,
                "type": "delivery",
            }
        )
        self.order.dest_address_id = delivery_partner
        self.assertEqual(
            self.order._jcdecaux_delivery_partner(), delivery_partner
        )

    def test_approval_lines_only_include_current_approved_round(self):
        self.order._write_purchase_approval_fields(
            {"purchase_approval_round": 2}
        )
        approval_values = {
            "order_id": self.order.id,
            "company_id": self.env.company.id,
            "approver_id": self.env.user.id,
            "acted_at": fields.Datetime.now(),
            "order_currency_id": self.order.currency_id.id,
            "order_amount": self.order.amount_total,
            "company_currency_id": self.env.company.currency_id.id,
            "company_amount": self.order.amount_total,
        }
        approvals = self.env["purchase.order.approval"].sudo().create(
            [
                {
                    **approval_values,
                    "round_number": 1,
                    "sequence": 1,
                    "role": "requester",
                    "state": "approved",
                },
                {
                    **approval_values,
                    "round_number": 2,
                    "sequence": 2,
                    "role": "financial_director",
                    "state": "approved",
                },
                {
                    **approval_values,
                    "round_number": 2,
                    "sequence": 1,
                    "role": "requester",
                    "state": "approved",
                },
                {
                    **approval_values,
                    "round_number": 2,
                    "sequence": 3,
                    "role": "general_director",
                    "state": "pending",
                    "approver_id": False,
                    "acted_at": False,
                },
            ]
        )

        report_approvals = self.order._jcdecaux_approval_lines()

        self.assertEqual(report_approvals.mapped("sequence"), [1, 2])
        self.assertEqual(
            report_approvals,
            approvals.filtered(
                lambda line: line.round_number == 2 and line.state == "approved"
            ).sorted("sequence"),
        )

    def test_report_action_is_bound_to_purchase_orders(self):
        report = self.env.ref(
            "jcdecaux_purchase_order_report.action_report_purchase_order_jcdecaux"
        )

        self.assertEqual(report.model, "purchase.order")
        self.assertEqual(report.report_type, "qweb-pdf")
        self.assertEqual(
            report.report_name,
            "jcdecaux_purchase_order_report.report_purchase_order_jcdecaux",
        )
        self.assertEqual(report.paperformat_id.format, "Letter")

    def test_native_purchase_reports_are_hidden_from_print_menu(self):
        native_report_xmlids = (
            "purchase.action_report_purchase_order",
            "purchase.report_purchase_quotation",
        )

        for xmlid in native_report_xmlids:
            with self.subTest(xmlid=xmlid):
                self.assertFalse(self.env.ref(xmlid).binding_model_id)

    def test_purchase_order_email_uses_jcdecaux_report(self):
        mail_template = self.env.ref(
            "purchase.email_template_edi_purchase_done"
        )
        report = self.env.ref(
            "jcdecaux_purchase_order_report.action_report_purchase_order_jcdecaux"
        )

        self.assertEqual(mail_template.report_template_ids, report)
