# Copyright (C) 2020 OdooERP România S.R.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class AccountCompensation(models.Model):
    _inherit = 'mail.thread'
    _name = 'account.compensation'
    _description = 'Debit Credit Compensation'

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(related='move_id.name', string='Name', readonly=True)
    date = fields.Date('Date', readonly=True)
    journal_id = fields.Many2one(
        'account.journal', 'Journal', required=True, readonly=True
    )
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    company_id = fields.Many2one(
        related='journal_id.company_id', readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True, readonly=True, default=_get_default_currency_id
    )
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    line_ids = fields.One2many(
        'account.compensation.line', 'compensation_id', 'Compensation Lines', readonly=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft')

    def action_done(self):
        self.write({
            'state': 'done'
        })

        val_error = ValidationError(_('The amount is... '))

        total = sum(line.amount for line in self.line_ids)
        if total != 0:
            raise val_error

        # for move_line in self.line_ids:
        #     to_reconcile = move_line + self.move_line_ids.filtered(
        #         lambda x: x.account_id == move_line.account_id
        #     )
        #     to_reconcile.reconcile()

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def action_cancelled(self):
        self.write({
            'state': 'cancel'
        })

    def write(self, vals):
        print(vals)
        super(AccountCompensation, self).write(vals)

    # @api.onchange('date', 'partner_id', 'journal_id')
    def onchange_for_all(self):
        comp_currency = self.env.user.company_id.currency_id
        # comp_line_obj = self.env['account.compensation.line']

        compensation = self[0]
        compensation.currency_id = compensation.journal_id.currency_id or \
                                   comp_currency

        lines = []

        compensation.line_ids.unlink()

        domain = [
            ('partner_id', '=', compensation.partner_id.id),
            ('date', '<=', fields.Date.from_string(compensation.date)),
            ('reconciled', '=', False),
            ('account_id.user_type_id.type', 'in', ('payable', 'receivable'))
        ]

        move_lines = self.env['account.move.line'].search(domain)
        for move in move_lines:
            if compensation.currency_id == comp_currency:
                amount_original = move.balance
                amount_residual = move.amount_residual
            elif compensation.currency_id == move.currency_id:
                amount_original = move.amount_currency
                amount_residual = move.amount_residual_currency
            else:
                amount_original = move.currency_id._convert(
                    move.amount_currency,
                    compensation.currency_id,
                    compensation.company_id,
                    move.date or fields.Date.today()
                )
                amount_residual = move.currency_id._convert(
                    move.amount_residual_currency,
                    compensation.currency_id,
                    compensation.company_id,
                    compensation.date or fields.Date.today()
                )

            lines.append((0, 0, {
                'move_line_id': move.id,
                'amount_original': amount_original,
                'amount_residual': amount_residual
            }))
        compensation.line_ids = lines
        print('\n\nSTART ***************************************')
        print(lines)
        print('END ***************************************\n\n')


class AccountCompensationLine(models.Model):
    _name = 'account.compensation.line'
    _description = 'Debit Credit Compensation Line'

    compensation_id = fields.Many2one('account.compensation', 'Compensation')
    company_id = fields.Many2one(
        related='compensation_id.company_id', string='Company',
        store=True
    )
    move_line_id = fields.Many2one(
        'account.move.line', 'Journal Item', copy=False
    )
    currency_id = fields.Many2one(
        related='move_line_id.currency_id', string='Currency',
        store=True
    )
    account_id = fields.Many2one(
        related='move_line_id.account_id', string='Account', required=True
    )
    partner_id = fields.Many2one(
        related='move_line_id.partner_id', string='Partner', readonly=True
    )
    date = fields.Date(
        related='move_line_id.date', string='Date', readonly=True
    )
    name = fields.Char(
        related='move_line_id.move_name', string='Name', readonly=True
    )
    amount_original = fields.Monetary(string='Original Amount')
    amount_residual = fields.Monetary(string='Residual Amount')
    amount = fields.Monetary(string='Amount')

    @api.onchange('amount')
    def onchange_amount(self):
        val_error = ValidationError(_('The amount is bigger than amount residual'))
        if self.amount_residual < 0:
            if self.amount < self.amount_residual or self.amount > 0:
                raise val_error
        else:
            if self.amount > self.amount_residual or self.amount < 0:
                raise val_error


