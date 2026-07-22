# JCDecaux Purchase Order Report

Odoo 17 add-on that provides the custom JCDecaux purchase order PDF layout.

## Installation

Add this repository to the Odoo add-ons path, update the Apps list, and install
`JCDecaux - Purchase Order Report` (`jcdecaux_purchase_order_report`).

The new **Orden de compra JCDecaux** option is available from the **Imprimir**
menu of a purchase order. The standard Odoo purchase report is not replaced.

## Configuration

The global purchase conditions can be changed under **Compras > Configuración >
Ajustes > Condiciones generales JCDecaux**. Access to this setting is restricted
to system administrators.

Payment terms are required on purchase orders so the report can always print
the corresponding condition.

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

## Pending approval integration

Approval history integration is intentionally deferred until the source module,
approval model, sequence, and technical fields are confirmed. The current report
prints the requester and order date but does not fabricate approval rows.
