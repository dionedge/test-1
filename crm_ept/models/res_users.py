
from odoo import models, api

class ResUsers(models.Model):
    _inherit='res.users'
    
    @api.model
    def create(self, vals):
        vals.update({'groups_id': [(6, 0, [18,77,1,39])]})
        return super(ResUsers, self).create(vals)