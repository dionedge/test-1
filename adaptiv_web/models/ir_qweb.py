import ast
from urllib.parse import urlparse
from lxml import html
from werkzeug import urls
import json

from odoo import models, api, tools
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.assetsbundle import AssetsBundle
from odoo.modules.module import get_resource_path
from odoo.tools import pycompat


class IrQWeb(models.AbstractModel):

    _inherit = 'ir.qweb'

    def _compile_directive_call_assets(self, el, options):
        if 't-theme' in el.attrib:
            theme = self._compile_expr(el.attrib.pop('t-theme'))
        else:
            theme = self._get_attr_bool(False)

        return [
            self._append(ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='_adaptiv_get_asset',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Str(el.get('t-call-assets')),
                    ast.Name(id='options', ctx=ast.Load()),
                ],
                keywords=[
                    ast.keyword('css', self._get_attr_bool(el.get('t-css', True))),
                    ast.keyword('js', self._get_attr_bool(el.get('t-js', True))),
                    ast.keyword('debug', ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='values', ctx=ast.Load()),
                            attr='get',
                            ctx=ast.Load()
                        ),
                        args=[ast.Str('debug')],
                        keywords=[], starargs=None, kwargs=None
                    )),
                    ast.keyword('async', self._get_attr_bool(el.get('async', False))),
                    ast.keyword('theme', theme),
                    ast.keyword('values', ast.Name(id='values', ctx=ast.Load())),
                ],
                starargs=None, kwargs=None
            ))
        ]

    @tools.conditional(
        # in non-xml-debug mode we want assets to be cached forever, and the admin can force a cache clear
        # by restarting the server after updating the source code (or using the "Clear server cache" in debug tools)
        'xml' not in tools.config['dev_mode'],
        tools.ormcache(
            'xmlid',
            'options.get("lang", "en_US")',
            'css',
            'js',
            'debug',
            'theme and theme["id"] or False',
            'async',
            keys=("website_id",)
        ),
    )
    def _adaptiv_get_asset(self, xmlid, options, css=True, js=True, debug=False, async=False, theme=False, values=None):
        asset_name = xmlid
        if theme:
            asset_name = '%s.theme.%s' % (xmlid, theme['id'])
        files, remains = self._adaptiv_get_asset_content(xmlid, options, theme=theme)
        asset = AssetsBundle(asset_name, files, remains, env=self.env)
        return asset.to_html(css=css, js=js, debug=debug, async=async, url_for=(values or {}).get('url_for', lambda url: url))

    @tools.ormcache('xmlid', 'options.get("lang", "en_US")', 'theme and theme["id"] or False', keys=("website_id",))
    def _adaptiv_get_asset_content(self, xmlid, options, theme=False):
        options = dict(options,
            inherit_branding=False, inherit_branding_auto=False,
            edit_translations=False, translatable=False,
            rendering_bundle=True)

        env = self.env(context=options)

        # TODO: This helper can be used by any template that wants to embedd the backend.
        #       It is currently necessary because the ir.ui.view bundle inheritance does not
        #       match the module dependency graph.
        def get_modules_order():
            if request:
                from odoo.addons.web.controllers.main import module_boot
                return json.dumps(module_boot())
            return '[]'
        template = env['ir.qweb'].render(xmlid, {"get_modules_order": get_modules_order, "theme": theme})

        files = []
        remains = []
        for el in html.fragments_fromstring(template):
            if isinstance(el, pycompat.string_types):
                remains.append(pycompat.to_text(el))
            elif isinstance(el, html.HtmlElement):
                href = el.get('href', '')
                src = el.get('src', '')
                atype = el.get('type')
                media = el.get('media')

                can_aggregate = not urls.url_parse(href).netloc and not href.startswith('/web/content')
                if el.tag == 'style' or (el.tag == 'link' and el.get('rel') == 'stylesheet' and can_aggregate):
                    if href.endswith('.sass'):
                        atype = 'text/sass'
                    elif href.endswith('.less'):
                        atype = 'text/less'
                    if atype not in ('text/less', 'text/sass'):
                        atype = 'text/css'
                    path = [segment for segment in href.split('/') if segment]
                    filename = get_resource_path(*path) if path else None
                    files.append({'atype': atype, 'url': href, 'filename': filename, 'content': el.text, 'media': media})
                elif el.tag == 'script':
                    atype = 'text/javascript'
                    path = [segment for segment in src.split('/') if segment]
                    filename = get_resource_path(*path) if path else None
                    files.append({'atype': atype, 'url': src, 'filename': filename, 'content': el.text, 'media': media})
                else:
                    remains.append(html.tostring(el, encoding='unicode'))
            else:
                try:
                    remains.append(html.tostring(el, encoding='unicode'))
                except Exception:
                    # notYETimplementederror
                    raise NotImplementedError

        return (files, remains)
