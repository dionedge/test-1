import logging
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import Warning
from xero.utils import OBJECT_NAMES

OBJECT_NAMES['PurchaseOrders'] = 'PurchaseOrder'

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    xero_exported = fields.Boolean('Xero Exported', default=False)
    xero_po_no = fields.Char('Xero Purchase Order Ref.')

    @api.one
    def copy(self, default=None):
        """ Inherited to set xero exported false when duplicate in record"""
        if not default:
            default = {}
        default.update({'xero_exported': False, 'xero_po_no': ''})
        return super(PurchaseOrder, self).copy(default=default)

    @api.multi
    def _get_purchase_lines(self, lines):
        """  Returns LineItems for Xero Invoice from Invoice Lines """
        lineitems = []
        for line in lines:
            line.product_id._check_product_exported()
            tax_code = ''
            if line.taxes_id:
                if len(line.taxes_id) > 1:
                    self.env['xero.logs'].create({'name': 'Multiple Tax for Purchase %s in product %s' % (self.name, line.name),
                                                  'purchaseorder_id': self.id,
                                                  'state': 'error',
                                                  'date': datetime.now()})
                    self._cr.commit()
                    raise Warning('Multiple taxes are not allowed in Xero.(%s) in product %s' % (self.name, line.name))
                else:
                    tax_code = line.taxes_id[0].xero_tax_type
            description = line.product_id.name
            line_dict = {
                'Description': description,
                'Quantity': str(line.product_qty),
                'UnitAmount': str(line.price_unit * (1 - (line.discount) / 100.0)) or '',
                'ItemCode': str(line.product_id.default_code),
            }
            if tax_code:
                line_dict['TaxType'] = tax_code
            lineitems.append(line_dict)
        return lineitems

    @api.multi
    def export_purchase_order(self, purchase_orders):
        """ Export Purchase Order's from OpenERP to Xero"""
        _logger.info("...Exporting Purchase Order's...")
        Purchase_list_dic = []
        purchase_obj_lst = []
        count = 0
        val = 1
        for purchase_order in purchase_orders:
            if not purchase_order.xero_exported:
                Purchase_dic = {'LineAmountTypes': 'Exclusive',
                                'LineItems': purchase_order._get_purchase_lines(purchase_order.order_line),
                                'Date': datetime.strptime(purchase_order.date_order[:10], '%Y-%m-%d'),
                                'Reference': purchase_order.name or '',
                                'CurrencyCode': purchase_order.currency_id.name,
                                'Contact': purchase_order.partner_id._get_contact()}
                Purchase_list_dic.append(Purchase_dic)
                purchase_obj_lst.append(purchase_order)
                count += 1
                if count == 100 * val:
                    self.xero_purchase_export(Purchase_list_dic, purchase_obj_lst)
                    Purchase_list_dic = []
                    val += 1
        if not count == 0:
            if Purchase_list_dic:
                self.xero_purchase_export(Purchase_list_dic, purchase_obj_lst)
                self.env['xero.logs'].create({'name': 'Successfully Exported Purchase Order to Xero',
                                              'state': 'success',
                                              'export_count': count,
                                              'date': datetime.now()})
                self._cr.commit()
        else:
            raise Warning('Purchase Order Already Exported!')

    @api.multi
    def xero_purchase_export(self, Purchase_list_dic, purchase_orders):
        company = self.env.user.company_id
        xero_client = company.get_xero_connection()
        response = False
        try:
            response = xero_client.purchaseorders.put(Purchase_list_dic)
            _logger.info('...Purchase Order exported successfully to Xero...')
        except Exception as e:
            _logger.info(e)
            message = ''
            if e:
                for error in e.errors:
                    message += "\n" + error
            self.env['xero.logs'].create({'name': 'Unable to Export %s' % (message),
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Unable to Export %s!' % (message))
        if response:
            for purchase_order in purchase_orders:
                filter_response = filter(lambda dic: dic['Reference'] == purchase_order.name, response)
                if filter_response[0]['PurchaseOrderNumber']:
                    purchase_order.write({
                        'xero_exported': True,
                        'xero_po_no': response[0]['PurchaseOrderNumber']
                    })
            self._cr.commit()
        self._cr.commit()

    @api.model
    def action_export_purchase_order_to_xero(self, purchase_ids):
        if purchase_ids:
            purchases_ids_obj = self.browse(purchase_ids)
            self.export_purchase_order(purchases_ids_obj)
