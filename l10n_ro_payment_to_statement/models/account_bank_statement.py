# Copyright (C) 2015-2020 Deltatech
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _name = "account.bank.statement"
    _inherit = ["account.bank.statement", "l10n.ro.mixin"]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.env.company._check_is_l10n_ro_record():
                if "name" not in vals or vals["name"] in ["/", "", False]:
                    journal = self.env["account.journal"].browse(vals["journal_id"])
                    if journal.l10n_ro_statement_sequence_id:
                        vals[
                            "name"
                        ] = journal.l10n_ro_statement_sequence_id.next_by_id()
                    else:
                        # sper sa nu fie doua statementuri in aceeasi zi
                        vals["name"] = fields.Date.to_string(fields.Date.today())
        return super().create(vals_list)

    def _compute_display_name(self):
        res = super()._compute_display_name()
        for record in self:
            if record.is_l10n_ro_record and record.name == "/":
                record.display_name = fields.Date.to_string(record.date)
        return res


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = ["account.bank.statement.line", "l10n.ro.mixin"]

    is_l10n_ro_payment_disposal = fields.Boolean()
