# Copyright (C) 2015 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from odoo import fields, models, tools


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_currency_rate_update_RO_BNR = fields.Boolean(
        "Currency Rate Update BNR",
        help="This option allows you to manage the update of currency "
        "rate based from BNR site.",
    )
    module_l10n_ro_address_extended = fields.Boolean(
        "Romanian Extended Address",
        help="Extend the  partner addres field with flat number, staircase..",
    )
    module_l10n_ro_siruta = fields.Boolean(
        "Romanian SIRUTA",
        help="This allows you to manage the Romanian Zones, States, "
        "Communes, Cities:\n The address fields will contain city, "
        "commune, state, zone, country, zip.",
    )
    siruta_update = fields.Boolean("Update Siruta Data")

    # Partners creation and Validations
    module_l10n_ro_partner_unique = fields.Boolean(
        "Partners unique by Company, VAT, NRC",
        help="This allows you to set unique partners by " "company, VAT and NRC.",
    )
    module_l10n_ro_partner_create_by_vat = fields.Boolean(
        "Create Partners by VAT",
        help="This allows you to create partners based on VAT:\n"
        "Romanian partners will be create based on ANAF webservice.\n"
        "European partners will be create based on VIES webservice "
        "(for countries that allow). \n",
    )
    module_l10n_ro_fiscal_validation = fields.Boolean(
        "Partners Fiscal Validation",
        help="This allows you to manage the vat subjected and vat on payment "
        "fields update:\n"
        "For Romanian partners based on ANAF webservice.\n"
        "For European partners based on VIES data.",
    )

    # Accounting Modules
    module_l10n_ro_vat_on_payment = fields.Boolean(
        "VAT_on_payment",
        help="This module will download data from ANAF site and when you "
        "give or receive a invoice will set fiscal position for VAT "
        "on payment",
    )
    module_l10n_ro_account_period_close = fields.Boolean(
        "Romania Account Period Close",
        help="This allows you to close accounts on periods based on "
        "templates: Income, Expense, VAT...",
    )

    # Accounting Reports
    module_l10n_ro_account_report_invoice = fields.Boolean(
        "Invoice Report",
        help="This allows you to print invoice report based on " "romanian layout.\n",
    )
    module_l10n_ro_account_report_trial_balance = fields.Boolean(
        "Account Trial Balance Report",
        help="This module will add the Trial Balance report " "with multiple columns.",
    )
    module_l10n_ro_account_report_journal = fields.Boolean(
        "Account Journal Reports",
        help="This module will add the Sale and Purchase Reports.",
    )
    module_l10n_ro_account_report_pl = fields.Boolean(
        "Account Profit and Loss Report",
        help="This module will add the Profit and Loss report.",
    )
    module_l10n_ro_account_report_balance_sheet = fields.Boolean(
        "Account Balance Sheet Report",
        help="This module will add the Balance Sheet report " "fetched from ANAF.",
    )
    module_l10n_ro_account_report_sheet = fields.Boolean(
        "Account Sheet Report", help="This module will add the Account Sheet report."
    )
    module_l10n_ro_account_report_journal_sheet = fields.Boolean(
        "Account Journal Sheet Report",
        help="This module will add the Journal Sheet report.",
    )
    module_l10n_ro_account_report_inventory_sheet = fields.Boolean(
        "Account Inventory Sheet Report",
        help="This module will add the Inventory Sheet report.",
    )
    module_l10n_ro_account_report_D300 = fields.Boolean(
        "Account D300 Report", help="This module will add the D300 report."
    )
    module_l10n_ro_account_report_D390 = fields.Boolean(
        "Account D390 Report", help="This module will add the D390 report."
    )
    module_l10n_ro_account_report_D394 = fields.Boolean(
        "Account D394 Report", help="This module will add the D394 report."
    )
    module_l10n_ro_account_report_intrastat = fields.Boolean(
        "Account Intrastat Report", help="This module will add the Intrastat report."
    )

    # stock section
    use_anglo_saxon = fields.Boolean(
        string="Anglo-Saxon Accounting",
        related="company_id.anglo_saxon_accounting",
        readonly=False,
    )
    module_l10n_ro_stock = fields.Boolean(
        "Romanian Stock",
        help="This module add on each warehouse methods of usage "
        "giving and consumption",
    )
    module_l10n_ro_stock_picking_report = fields.Boolean(
        "Stock Picking Report",
        help="This allows you to print Reports for Reception and Delivery",
    )
    module_l10n_ro_stock_account = fields.Boolean(
        "Romanian Stock Accounting",
        help="This allows you to manage the Romanian adaptation for stock, "
        "including:\n"
        "New stock accounts on location to allow moving entry in "
        "accounting based on the stock move.\n"
        "The account entry will be generated from stock move instead of "
        "stock quant, link with the generated account move lines on the "
        "picking\n"
        "Inventory account move lines...",
    )
    property_stock_picking_payable_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_picking_payable_account_id",
        readonly=False,
    )
    property_stock_picking_receivable_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_picking_receivable_account_id",
        readonly=False,
    )
    property_stock_usage_giving_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_usage_giving_account_id",
        readonly=False,
    )
    property_stock_picking_custody_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_picking_custody_account_id",
        readonly=False,
    )
    property_uneligible_tax_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_uneligible_tax_account_id",
        readonly=False,
    )
    property_stock_transfer_account_id = fields.Many2one(
        "account.account",
        related="company_id.property_stock_transfer_account_id",
        readonly=False,
    )

    def execute(self):
        self.ensure_one()
        res = super(ResConfigSettings, self).execute()
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

        # Load SIRUTA datas if field is checked
        if self.siruta_update:
            # First check if module is installed
            installed = self.env["ir.module.module"].search(
                [("name", "=", "l10n_ro_siruta"), ("state", "=", "installed")]
            )
            if installed:
                path = data_dir + "/l10n_ro_siruta/"
                files = [
                    "res.country.zone.csv",
                    "res.country.state.csv",
                    "res.country.commune.csv",
                    "res.country.city.csv",
                ]
                for file1 in files:
                    with tools.file_open(path + file1) as fp:
                        tools.convert_csv_import(
                            self._cr,
                            "l10n_ro_config",
                            file1,
                            fp.read(),
                            {},
                            mode="init",
                            noupdate=True,
                        )
        return res