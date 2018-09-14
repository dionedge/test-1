
from odoo import api, models

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:
            name = account.code + ' ' + account.name + '' + '' + '(' + account.company_id.name + ')'
            result.append((account.id, name))
        return result