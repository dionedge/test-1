from odoo import models, api
from odoo.http import request


class View(models.Model):

    _inherit = 'ir.ui.view'

    @api.model
    def get_theme(self):
        if not (request and request.debug == 'assets'):
            return self.env['res.company'].get_current().get_theme()

    @api.multi
    def render(self, values=None, engine='ir.qweb'):
        values = values or {}
        # Since this variable will be available in every template
        # prefix it with adaptiv_
        values.update({
            'adaptiv_get_theme': self.get_theme
        })

        return super(View, self).render(values=values, engine=engine)

