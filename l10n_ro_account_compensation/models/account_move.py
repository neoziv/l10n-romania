# Copyright (C) 2020 OdooERP România S.R.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    compensation_line_id = fields.Many2one(
        'account.compensation.line', string='Compensation Line', readonly=True
    )

