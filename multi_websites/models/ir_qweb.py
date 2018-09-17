# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models
from .website import MULTI_ASSETS
from odoo.tools import html_escape as escape
from odoo.tools import ustr, pycompat
import ast
import logging
_logger = logging.getLogger(__name__)
class IrQweb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _get_asset(self, xmlid, *args, **kwargs):
        website_id = self.env.context.get("website_id")
        if xmlid == "web.assets_frontend" and website_id:
            alt_xmlid = MULTI_ASSETS % website_id
            if self.env.ref(alt_xmlid, False):
                xmlid = alt_xmlid
        return super(IrQweb, self)._get_asset(xmlid, *args, **kwargs)


    def _compile_directive_snippet(self, el, options):
        el.set('t-call', el.attrib.pop('t-snippet'))
        _logger.info('----------options------%r',options)
        _logger.info('----------el------%r',el)
        recs = self.env['ir.ui.view'].search([('key', '=', el.attrib.get('t-call'))])
        for rec in recs:
            name = rec.display_name
            _logger.info('----------name------%r',name)
            thumbnail = el.attrib.pop('t-thumbnail', "oe-thumbnail")
            div = u'<div name="%s" data-oe-type="snippet" data-oe-thumbnail="%s">' % (
                escape(pycompat.to_text(name)),
                escape(pycompat.to_text(thumbnail))
            )
            return [self._append(ast.Str(div))] + self._compile_node(el, options) + [self._append(ast.Str(u'</div>'))]