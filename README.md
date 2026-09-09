# JCDecaux Purchase Order Report

Odoo 17 add-on that provides the custom JCDecaux purchase order PDF layout.

## Installation

Add this repository to the Odoo add-ons path, update the Apps list, and install
`JCDecaux - Purchase Order Report` (`jcdecaux_purchase_order_report`).

The **Orden de compra JCDecaux** option is the only report shown in the
**Imprimir** menu. Odoo's native purchase-order and request-for-quotation reports
remain available internally but are hidden from that menu.
When a confirmed purchase order is sent by email through Odoo's standard
**Send PO** action, the JCDecaux report replaces the native PDF attachment.

## Configuration

The global purchase conditions can be changed under **Compras > Configuración >
Ajustes > Condiciones generales JCDecaux**. Access to this setting is restricted
to system administrators.

Payment terms are required on purchase orders so the report can always print
the corresponding condition.

### Additional PDF

System administrators can upload an additional PDF under **Compras >
Configuración > Ajustes > PDF adicional para la orden de compra JCDecaux**.
The file is configured independently per company. Its pages are appended after
the purchase order whenever the JCDecaux report is printed or attached to an
email. If no file is configured, the report is generated without an appendix.
The custom purchase order uses A4 paper so its page dimensions match the
standard additional document.

## Amount mapping

The report uses Odoo's computed purchase values and does not hard-code a tax
percentage:

| Printed value | Odoo field |
| --- | --- |
| Unit value | `purchase.order.line.price_unit` |
| VAT per line | `purchase.order.line.price_tax` |
| Line value before tax | `purchase.order.line.price_subtotal` |
| Subtotal | `purchase.order.amount_untaxed` |
| VAT total | `purchase.order.amount_tax` |
| Purchase total | `purchase.order.amount_total` |

Line notes are printed in the observations section. The supplier code currently
uses `res.partner.ref`; this can be changed to the SAP field after its technical
name is confirmed.

## Approval integration

The add-on depends on `jcdecaux_purchase_approval`. The final report block prints
only approved records from the current approval round, ordered by sequence. Each
signature includes the user who acted and its date and time.
Rejected, cancelled, pending, and previous-round records are not printed.
