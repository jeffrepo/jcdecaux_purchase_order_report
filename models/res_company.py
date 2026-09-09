import base64
import binascii
import io

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.pdf import PdfFileReader, PdfReadError


class ResCompany(models.Model):
    _inherit = "res.company"

    jcdecaux_purchase_appendix_pdf = fields.Binary(
        string="PDF adicional para órdenes de compra JCDecaux",
        attachment=True,
        copy=False,
    )
    jcdecaux_purchase_appendix_filename = fields.Char(
        string="Nombre del PDF adicional",
        copy=False,
    )

    @api.constrains("jcdecaux_purchase_appendix_pdf")
    def _check_jcdecaux_purchase_appendix_pdf(self):
        for company in self.filtered("jcdecaux_purchase_appendix_pdf"):
            try:
                pdf_content = base64.b64decode(
                    company.jcdecaux_purchase_appendix_pdf,
                    validate=True,
                )
                if b"%PDF-" not in pdf_content[:1024]:
                    raise PdfReadError("Missing PDF header")
                reader = PdfFileReader(io.BytesIO(pdf_content), strict=False)
                if not reader.numPages:
                    raise PdfReadError("PDF has no pages")
            except (
                AttributeError,
                binascii.Error,
                KeyError,
                NotImplementedError,
                OSError,
                PdfReadError,
                TypeError,
                ValueError,
            ) as error:
                raise ValidationError(
                    _(
                        "El archivo adicional debe ser un PDF válido, con al "
                        "menos una página y sin contraseña."
                    )
                ) from error
