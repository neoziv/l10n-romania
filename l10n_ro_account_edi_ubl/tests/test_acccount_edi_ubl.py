# Copyright (C) 2020 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging

from odoo import fields
from odoo.modules.module import get_module_resource
from odoo.tests import tagged

from odoo.addons.account_edi.tests.common import AccountEdiTestCommon

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestAccountEdiUbl(AccountEdiTestCommon):
    @classmethod
    def setUpClass(cls):
        ro_template_ref = "l10n_ro.ro_chart_template"
        super().setUpClass(chart_template_ref=ro_template_ref)
        cls.env.company.l10n_ro_accounting = True
        cls.currency = cls.env["res.currency"].search([("name", "=", "RON")])
        cls.country_state = cls.env.ref("base.RO_TM")

        cls.env.company.write(
            {
                "vat": "RO30834857",
                "name": "FOREST AND BIOMASS ROMÂNIA S.A.",
                "country_id": cls.env.ref("base.ro").id,
                "currency_id": cls.currency.id,
                "street": "Ferma 5-6",
                "street2": "Zona Nr.3, Etaj 1",
                "city": "Giulvaz",
                "state_id": cls.country_state.id,
                "zip": "300011",
                "phone": "0356179038",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "SCOALA GIMNAZIALA COMUNA FOENI",
                "ref": "SCOALA GIMNAZIALA COMUNA FOENI",
                "vat": "29152430",
                "country_id": cls.env.ref("base.ro").id,
                "l10n_ro_vat_subjected": False,
                "street": "Foeni Nr. 383",
                "city": "Sat Foeni Com Foeni",
                "state_id": cls.country_state.id,
                "zip": "307175",
                "phone": "0256413409",
                "l10n_ro_e_invoice": True,
                "l10n_ro_is_government_institution": True,
            }
        )

        uom_id = cls.env.ref("uom.product_uom_unit").id
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Bec P21/5W",
                "default_code": "00000623",
                "type": "product",
                "uom_id": uom_id,
                "uom_po_id": uom_id,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Bec P21/10W",
                "default_code": "00000624",
                "type": "product",
                "uom_id": uom_id,
                "uom_po_id": uom_id,
            }
        )
        cls.tax_19 = cls.env["account.tax"].create(
            {
                "name": "tax_19",
                "amount_type": "percent",
                "amount": 19,
                "type_tax_use": "sale",
                "sequence": 19,
                "company_id": cls.env.company.id,
            }
        )
        invoice_values = {
            "move_type": "out_invoice",
            "name": "FBRAO2092",
            "partner_id": cls.partner.id,
            "invoice_date": fields.Date.from_string("2022-09-01"),
            "currency_id": cls.currency.id,
            "invoice_line_ids": [
                (
                    0,
                    None,
                    {
                        "product_id": cls.product_a.id,
                        "name": "[00000623] Bec P21/5W",
                        "quantity": 5,
                        "price_unit": 1000.00,
                        "tax_ids": [(6, 0, cls.tax_19.ids)],
                    },
                ),
                (
                    0,
                    None,
                    {
                        "product_id": cls.product_b.id,
                        "name": "[00000624] Bec P21/10W",
                        "quantity": 5,
                        "price_unit": 1000.00,
                        "tax_ids": [(6, 0, cls.tax_19.ids)],
                    },
                ),
            ],
        }
        cls.invoice = cls.env["account.move"].create(invoice_values)

        invoice_values.update(
            {
                "move_type": "out_refund",
                "name": "FBRAO2093",
            }
        )
        cls.credit_note = cls.env["account.move"].create(invoice_values)

        test_file_path = get_module_resource(
            "l10n_ro_account_edi_ubl", "tests", "invoice.xml"
        )
        cls.expected_invoice_values = open(test_file_path).read().encode("utf-8")

        test_file_path = get_module_resource(
            "l10n_ro_account_edi_ubl", "tests", "credit_note.xml"
        )
        cls.expected_credit_note_values = open(test_file_path).read().encode("utf-8")

    def test_account_invoice_edi_ubl(self):
        self.invoice.action_post()
        invoice_xml = self.invoice.attach_ubl_xml_file_button()
        att = self.env["ir.attachment"].browse(invoice_xml["res_id"])
        xml_content = base64.b64decode(att.with_context(bin_size=False).datas)

        current_etree = self.get_xml_tree_from_string(xml_content)
        expected_etree = self.get_xml_tree_from_string(self.expected_invoice_values)

        self.assertXmlTreeEqual(current_etree, expected_etree)

    def test_account_credit_note_edi_ubl(self):
        self.credit_note.action_post()
        invoice_xml = self.credit_note.attach_ubl_xml_file_button()
        att = self.env["ir.attachment"].browse(invoice_xml["res_id"])
        xml_content = base64.b64decode(att.with_context(bin_size=False).datas)

        current_etree = self.get_xml_tree_from_string(xml_content)
        expected_etree = self.get_xml_tree_from_string(self.expected_credit_note_values)
        self.assertXmlTreeEqual(current_etree, expected_etree)
