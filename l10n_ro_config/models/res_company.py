# Copyright (C) 2015 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    share_capital = fields.Float(string="Share Capital", digits="Account", default=200)
    company_registry = fields.Char(related="partner_id.nrc", readonly=False)
    property_stock_picking_payable_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Payable",
        domain="[('internal_type', 'in', ['payable','other'])]",
        help="This account will be used as the payable account for the "
        "current partner on stock picking notice.",
    )
    property_stock_picking_receivable_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Receivable",
        domain="[('internal_type', 'in', ['receivable','other'])]",
        help="This account will be used as the receivable account for the "
        "current partner on stock picking notice.",
    )
    property_stock_usage_giving_account_id = fields.Many2one(
        "account.account",
        string="Usage Giving Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the usage giving "
        "account in account move line.",
    )
    property_stock_picking_custody_account_id = fields.Many2one(
        "account.account",
        string="Picking Account Custody",
        help="This account will be used as the extra trial balance payable "
        "account for the current partner on stock picking received "
        "in custody.",
    )
    property_uneligible_tax_account_id = fields.Many2one(
        "account.account",
        string="Not Eligible Tax Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as the not eligible tax account for "
        "account move line.\nUsed in especially in inventory losses.",
    )
    property_stock_transfer_account_id = fields.Many2one(
        "account.account",
        string="Company Stock Trabnsfer Account",
        domain="[('internal_type', '=', 'other')]",
        help="This account will be used as an intermediary account for "
        "account move line generated from internal moves between company "
        "stores.",
    )
