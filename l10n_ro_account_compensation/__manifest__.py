# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Compensation',
    'summary': 'Compensate partners credits and debits',
    'version': '13.0.1.0.0',
    'category': 'Accounting & Finance',
    'sequence': 4,
    'author': 'OdooERP România S.R.L., '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-romania',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        # views
        'views/account_compensation_view.xml',
        # data

        # report

        # model access
        'security/ir.model.access.csv'
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
    'development_status': 'Mature',
    'maintainers': [
        'feketemihai',
        'horjarobert'
    ]
}
