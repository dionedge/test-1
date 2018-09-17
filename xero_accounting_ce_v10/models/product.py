import logging
from datetime import datetime
from random import randint

from odoo import models, fields, api
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _inherit = "product.product"

    @api.multi
    def _check_product_exported(self):
        company_id = self.env.user.company_id.id
        product_export_id = self.env['exported.product'].search([('company_id', '=', company_id), ('product_id', '=', self.id),
                                                                 ('xero_update', '=', True)])
        if not product_export_id:
            self.export_product()
            self.env['xero.logs'].create({'name': 'Exported/Update Product %s! to Xero' % (self.name),
                                          'product_id': self.id,
                                          'state': 'success',
                                          'date': datetime.now()})
        return True

    @api.one
    def _get_sales_details_product(self):
        income_account = False
        if self.property_account_income_id:
            income_account = self.property_account_income_id.code
        if not income_account and self.categ_id and self.categ_id.property_account_income_categ_id:
            income_account = self.categ_id.property_account_income_categ_id.code
        if not income_account:
            self.env['xero.logs'].create({'name': 'Income Account is not set for product %s! to Xero' % (self.name),
                                          'product_id': self.id,
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Income Account is not set for product ' + self.name)
        return {
            'UnitPrice': str(self.lst_price) or '0.0',
            'AccountCode': income_account,
        }

    @api.one
    def _get_purchase_details_product(self):

        expense_account = self.property_account_expense_id and self.property_account_expense_id.code or False
        if not expense_account and self.categ_id and self.categ_id.property_account_expense_categ_id:
            expense_account = self.categ_id.property_account_expense_categ_id.code
        if not expense_account:
            self.env['xero.logs'].create({'name': 'Expense Account is not set for product %s! to Xero' % (self.name),
                                          'product_id': self.id,
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            Warning('Expense  Account is not set for product ' + self.name)
        return {
            'UnitPrice': str(self.standard_price) or '0.0',
            'AccountCode': expense_account,
        }

    @api.model
    def copy(self, default=None):
        """ Set empty default_code"""
        if not default:
            default = {}
        default.update({'default_code': ''})
        return super(product_product, self).copy(default=default)

    @api.multi
    def write(self, vals):
        """ If Changes some fields of product then set xero_update to False """
        ids = [rec.id for rec in self]
        if vals.get('list_price') or vals.get('standard_price') or vals.get('name') or vals.get('default_code'):
            exp_prod_ids = self.env['exported.product'].search([('product_id', 'in', ids)])  # ('company_id', '=', company_id),
            if exp_prod_ids:
                exp_prod_ids.write({'xero_update': False})
        return super(product_product, self).write(vals)

    @api.multi
    def export_product(self):
        """ Export Product from OpenERP to Xero"""
        company = self.env['res.users'].browse(self._uid).company_id
        xero_client = company.get_xero_connection()
        exp_prod_obj = self.env['exported.product']
        exported_prod_id = False
        # validation for name_lenght cannot be greater than 50 char.
        sliced_name = self.name[:48] if len(self.name) > 48 else self.name
        exported_prod = exp_prod_obj.search([('product_id', '=', self.id), ('xero_update', '=', False)])
        if not self.default_code:
            self.env['xero.logs'].create({'name': 'Internal reference not provide to Product %s!' % (self.name),
                                          'product_id': self.id,
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Please set Internal reference for the %s' % (self.name))

        # if product is available in the reference table i.e, exported_product
        if exported_prod and len(exported_prod) == 1:
            exported_prod_id = exported_prod.xero_product_id or False
            if exported_prod_id:
                items_xero = xero_client.items.get(exported_prod_id)
                items_xero[0].update({'Code': self.default_code,
                                      'Name': sliced_name,
                                      'Description': self.description_sale or self.name,
                                      'PurchaseDescription': self.description_purchase or self.name,
                                      'IsSold': 0,
                                      'IsPurchased': 0,
                                      'IsTrackedAsInventory': 0
                                      })
                if self.sale_ok:
                    items_xero[0]['SalesDetails'] = self._get_sales_details_product()[0]
                    items_xero[0]['IsSold'] = 1
                if self.purchase_ok:
                    items_xero[0]['PurchaseDetails'] = self._get_purchase_details_product()[0]
                    items_xero[0]['IsPurchased'] = 1
                items_xero[0]['IsTrackedAsInventory'] = 0

                try:
                    response = xero_client.items.save(items_xero)
                    _logger.info('...Product %s Update successfully to Xero...' % self.name)
                except Exception as e:
                    _logger.info(e)
                    message = ''
                    if e:
                        for error in e.errors:
                            message += "\n" + error
                    self.env['xero.logs'].create({'name': 'Unable to Update Product %s! to Xero' % (self.name),
                                                  'product_id': self.id,
                                                  'state': 'error',
                                                  'date': datetime.now()})
                    self._cr.commit()
                    raise Warning('Unable to Update %s!\n%s' % (self.name, message))
                if response:
                    xero_product_id = response[0]['ItemID']
                    updated_product_ids = exp_prod_obj.search([('xero_product_id', '=', xero_product_id)])
                    if updated_product_ids:
                        updated_product_ids.write({
                            'xero_update': True,
                        })

                    self._cr.commit()

        # Else if product is available in odoo and xero but not available in the reference table.
        else:
            _logger.info('...Exporting Products...')

            try:
                if xero_client.items.get(self.default_code):
                    items_xero = xero_client.items.get(self.default_code)
                    if items_xero:
                        prod_id_search = self.env['product.product'].search([('default_code', '=', self.default_code)])
                        if prod_id_search:
                            company_id = self.env.user.company_id.id

                            res = exp_prod_obj.create({
                                'xero_product_id': items_xero[0]['ItemID'],
                                'product_id': prod_id_search.id,
                                'xero_update': True,
                                'company_id': company_id
                            })
                            exported_prod = res

                            items_xero[0].update({'Code': self.default_code,
                                                  'Name': sliced_name,
                                                  'Description': self.description_sale or self.name,
                                                  'PurchaseDescription': self.description_purchase or self.name,
                                                  'IsSold': 0,
                                                  'IsPurchased': 0,
                                                  'IsTrackedAsInventory': 0
                                                  })
                            if self.sale_ok:
                                items_xero[0]['SalesDetails'] = self._get_sales_details_product()[0]
                                items_xero[0]['IsSold'] = 1
                            if self.purchase_ok:
                                items_xero[0]['PurchaseDetails'] = self._get_purchase_details_product()[0]
                                items_xero[0]['IsPurchased'] = 1
                            items_xero[0]['IsTrackedAsInventory'] = 0

                            try:
                                response = xero_client.items.save(items_xero)
                                _logger.info('...Product %s Update successfully to Xero...' % self.name)
                            except Exception as e:
                                _logger.info(e)
                                message = ''
                                if e:
                                    for error in e.errors:
                                        message += "\n" + error
                                self.env['xero.logs'].create({'name': 'Unable to Update Product %s! to Xero' % (self.name),
                                                              'product_id': self.id,
                                                              'state': 'error',
                                                              'date': datetime.now()})
                                self._cr.commit()
                                raise Warning('Unable to Update %s!\n%s' % (self.name, message))

                                # Else if product is not available in both reference table and xero
            except Exception as  e:
                self._cr.commit()
                Item_dic = {'Code': self.default_code,
                            'Name': sliced_name,
                            'Description': self.description_sale or self.name,
                            'PurchaseDescription': self.description_purchase or self.name}
                if self.sale_ok:
                    Item_dic.update({'SalesDetails': self._get_sales_details_product()[0]})
                if self.purchase_ok:
                    Item_dic.update({'PurchaseDetails': self._get_purchase_details_product()[0]})
                try:
                    response = xero_client.items.put(Item_dic)
                    _logger.info('...Product %s exported successfully to Xero...' % self.name)
                except Exception as e:
                    _logger.info(e)
                    message = ''
                    if e:
                        for error in e.errors:
                            message += "\n" + error
                            if 'Code' + self.default_code + 'already exists':
                                pass
                    res = self.env['xero.logs'].create({'name': 'Unable to Export Product %s! to Xero' % (self.name),
                                                        'product_id': self.id,
                                                        'state': 'error',
                                                        'date': datetime.now()})
                    self._cr.commit()
                    raise Warning('Unable to Export %s!\n%s' % (self.name, message))
                if response:
                    xero_product_id = response[0]['ItemID']

                    updated_product_ids = exp_prod_obj.search([('xero_product_id', '=', xero_product_id)])
                    if updated_product_ids:
                        updated_product_ids.write({
                            'xero_update': True,
                        })
                    else:
                        exp_prod_obj.create({
                            'company_id': company.id,
                            'product_id': self.id,
                            'xero_product_id': xero_product_id,
                            'xero_update': True,
                        })
                    self._cr.commit()
        self._cr.commit()
        return True


class exported_product(models.Model):
    _name = "exported.product"

    company_id = fields.Many2one('res.company', 'Company', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    xero_product_id = fields.Char('Xero Product Id', size=256, required=True)
    xero_update = fields.Boolean('Xero Update')
