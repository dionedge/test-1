from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

import re


COLOR_HEX_REGEX = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')



def _check_color(value):
    if value and not COLOR_HEX_REGEX.match(value):
        raise ValidationError(_("Not a valid color"))


class ResCompany(models.Model):

    _inherit = 'res.company'

    svg_logo = fields.Binary("Logo (svg)", attachment=True,
        help="This field holds the SVG file used as a logo.")
    svg_logo_inverse = fields.Binary("Logo inverse (svg)", attachment=True,
        help="This field holds the SVG file used as an inverse logo. "
        "The inverse logo is displayed in the sidebar.")
    png_logo = fields.Binary("Logo (png)", attachment=True,
        help="This field holds the PNG image used as a logo.")
    png_logo_inverse = fields.Binary("Logo inverse (png)", attachment=True,
        help="This field holds the PNG image used as an inverse logo. "
        "This logo is displayed in the sidebar.")

    color_primary = fields.Char(string="Primary color", size=7)
    color_optional = fields.Char(string="Optional color", size=7)
    color_success = fields.Char(string="Success color", size=7)
    color_warning = fields.Char(string="Warning color", size=7)
    color_danger= fields.Char(string="Danger color", size=7)
    color_info = fields.Char(string="Info color", size=7)

    @api.multi
    @api.constrains('color_primary')
    def _check_color_primary(self):
        for company in self:
            _check_color(company.color_primary)

    @api.multi
    @api.constrains('color_optional')
    def _check_color_optional(self):
        for company in self:
            _check_color(company.color_optional)

    @api.multi
    @api.constrains('color_success')
    def _check_color_success(self):
        for company in self:
            _check_color(company.color_success)

    @api.multi
    @api.constrains('color_warning')
    def _check_color_warning(self):
        for company in self:
            _check_color(company.color_warning)

    @api.multi
    @api.constrains('color_danger')
    def _check_color_danger(self):
        for company in self:
            _check_color(company.color_danger)

    @api.multi
    @api.constrains('color_info')
    def _check_color_info(self):
        for company in self:
            _check_color(company.color_info)

    @api.model
    def get_current(self):
        user = self.env.user
        if not user or user.company_id is False:
            # Get superuser
            user = self.sudo().env.user
        return user.company_id

    @api.multi
    def get_theme(self):
        self.ensure_one()
        theme = {
            'id': self.id
        }
        values = self.read([
            'color_primary',
            'color_optional',
            'color_success',
            'color_warning',
            'color_danger',
            'color_info'
        ])

        theme.update({
            'brand-%s' % key.split('color_')[1]: val
            for key, val in values[0].items()
            if key.startswith('color_') and val
        })

        if 'brand-optional' not in theme and 'brand-primary' in theme:
            theme['brand-optional'] = theme['brand-primary']

        return theme
