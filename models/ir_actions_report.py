import base64
import io

from odoo import models


JCDECAUX_PURCHASE_REPORT_NAME = (
    "jcdecaux_purchase_order_report.report_purchase_order_jcdecaux"
)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        streams = super()._render_qweb_pdf_prepare_streams(
            report_ref,
            data,
            res_ids=res_ids,
        )
        report = self._get_report(report_ref)
        if report.report_name != JCDECAUX_PURCHASE_REPORT_NAME or not res_ids:
            return streams

        return self._jcdecaux_append_purchase_pdf(streams, report, res_ids)

    def _jcdecaux_append_purchase_pdf(self, streams, report, res_ids):
        """Append each order company's configured PDF to its report stream."""
        if report.report_name != JCDECAUX_PURCHASE_REPORT_NAME:
            return streams

        orders = self.env["purchase.order"].browse(res_ids).exists()
        for order in orders:
            stream_data = streams.get(order.id)
            purchase_stream = stream_data and stream_data.get("stream")
            appendix_pdf = (
                order.company_id.sudo().jcdecaux_purchase_appendix_pdf
            )
            if not purchase_stream or not appendix_pdf:
                continue

            purchase_stream.seek(0)
            appendix_stream = io.BytesIO(base64.b64decode(appendix_pdf))
            try:
                merged_stream = self._merge_pdfs(
                    [purchase_stream, appendix_stream]
                )
            finally:
                appendix_stream.close()

            purchase_stream.close()
            stream_data["stream"] = merged_stream

        return streams
