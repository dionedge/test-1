
from odoo import api, models,fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    @api.multi
    @api.depends('name', 'currency_id', 'company_id', 'company_id.currency_id')
    def name_get(self):
        result = []
        for journal in self:
            currency = journal.currency_id or journal.company_id.currency_id
            company_name = journal.company_id
            name = "%s (%s) (%s)" % (journal.name, currency.name, company_name.name)
            result += [(journal.id, name)]
        return result
    
class account_payment(models.Model):
    _inherit= 'account.payment'
    
    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            if invoice['company_id']:
                rec['company_id'] = invoice['company_id'][0]
            
        return rec
         
    @api.onchange('company_id')
    def onchange_company(self):
        if not self.company_id:
            self.company_id = self.env.user.company_id.id
        domain = [('type', 'in', ('bank', 'cash')),('company_id','=',self.company_id.id)]
        self.journal_id = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),('company_id','=',self.company_id.id)],limit=1).id or False
        return {'domain':{'journal_id':domain}}

class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    company_id = fields.Many2one('res.company',related=False, string='Company',readonly=False)

