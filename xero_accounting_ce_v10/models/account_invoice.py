#  -*- encoding: utf-8 -*-
import logging
from datetime import datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)
from odoo.exceptions import Warning


class account_invoice(models.Model):
    """ Inherited to add new field """
    _inherit = 'account.invoice'

    xero_exported = fields.Boolean('Xero Exported')
    xero_invoice_no = fields.Char('Xero Invoice Number', size=128)
    xero_invoice_id = fields.Char('Xero Invoice ID', size=128)

    @api.one
    def _get_invoice_lines(self, lines):
        """  Returns LineItems for Xero Invoice from Invoice Lines """
        lineitems = []
        for line in lines:
            line.product_id._check_product_exported()

            tax_code = ''
            if line.invoice_line_tax_ids:
                if len(line.invoice_line_tax_ids) > 1:
                    self.env['xero.logs'].create({'name': 'Multiple Tax for Invoice %s in product %s' % (self.number, line.name),
                                                  'invoice_id': self.id,
                                                  'state': 'error',
                                                  'date': datetime.now()
                                                  })
                    self._cr.commit()
                    raise Warning('Multiple taxes are not allowed in Xero.(%s) in product %s' % (self.number, line.name))
                else:
                    tax_code = line.invoice_line_tax_ids[0].xero_tax_type
            line_dict = {
                'Description': line.name,
                'Quantity': str(line.quantity),
                'UnitAmount': str(line.price_unit),
                'AccountCode': line.account_id.code,
                'ItemCode': str(line.product_id.default_code),
            }
            if line.invoice_id.type == 'out_invoice':
                line_dict.update({'DiscountRate': str(line.discount) or '',})
            if line.invoice_id.type == 'in_invoice':
                line_dict.update({'UnitAmount': str(line.price_unit * (1 - (line.discount) / 100.0)) or '',})
            if tax_code:
                line_dict['TaxType'] = tax_code
            lineitems.append(line_dict)
        return lineitems

    @api.one
    def copy(self, default=None):
        """ Inherited to set xero exported false when duplicate in record"""
        if not default:
            default = {}
        default.update({'xero_exported': False, 'xero_invoice_no': ''})
        return super(account_invoice, self).copy(default=default)

    @api.multi
    def export_invoices(self, invoices):
        """  Exporting selected invoices to Xero Account """
        _logger.info('...Exporting Invoices...')
        count = 0
        val = 1
        invoice_obj_lst = []
        Invoice_list_dic = []
        for invoice in invoices:
            if invoice.state == 'open' and not invoice.xero_exported:

                Invoice_dic = {'LineAmountTypes': 'Exclusive',
                               'LineItems': invoice._get_invoice_lines(invoice.invoice_line_ids)[0],
                               'Type': invoice.type == 'out_invoice' and 'ACCREC' or 'ACCPAY',
                               'Date': datetime.strptime(invoice.date_invoice, '%Y-%m-%d'),
                               'Reference': [invoice.name + '-' + invoice.number if invoice.name else invoice.number][0],
                               'CurrencyCode': invoice.currency_id.name,
                               'Status': 'DRAFT',
                               'Contact': invoice.partner_id.parent_id and invoice.partner_id.parent_id._get_contact() or invoice.partner_id._get_contact()}
                if invoice.type == 'in_invoice':
                    Invoice_dic.update({'InvoiceNumber': [invoice.reference + '-' + invoice.number if invoice.reference else invoice.number][0]})

                if invoice.date_due:
                    Invoice_dic.update({'DueDate': datetime.strptime(invoice.date_due, '%Y-%m-%d')})
                Invoice_list_dic.append(Invoice_dic)
                invoice_obj_lst.append(invoice)
                count += 1
                if count == 100 * val:
                    self.xero_invoice_export(Invoice_list_dic, invoice_obj_lst)
                    Invoice_list_dic = []
                    val += 1
        if not count == 0:
            if Invoice_list_dic:
                self.xero_invoice_export(Invoice_list_dic, invoice_obj_lst)
                self.env['xero.logs'].create({'name': 'Successfully Exported Invoice to Xero',
                                              'state': 'success',
                                              'export_count': count,
                                              'date': datetime.now()})
                self._cr.commit()
        else:
            raise Warning('Invoice Already Exported!')

    @api.multi
    def xero_invoice_export(self, Invoice_list_dic, invoices):
        """ Common method for export invoice """
        company = self.env.user.company_id
        xero_client = company.get_xero_connection()
        response = False
        try:
            response = xero_client.invoices.put(Invoice_list_dic)
            _logger.info('...Invoice exported successfully to Xero...')
        except Exception as e:
            _logger.info(e)
            message = ''
            if e:
                for error in e.errors:
                    message += "\n" + error
            self.env['xero.logs'].create({'name': 'Unable to Export! %s' % (message),
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Unable to Export!\n%s' % (message))
        if response:
            for invoice in invoices:
                if invoice.type == 'out_invoice':
                    filter_response = filter(
                        lambda dic: dic['Reference'] == [invoice.name + '-' + invoice.number if invoice.name else invoice.number][0], response)
                if invoice.type == 'in_invoice':
                    filter_response = filter(
                        lambda dic: dic['InvoiceNumber'] == [invoice.reference + '-' + invoice.number if invoice.reference else invoice.number][0],
                        response)
                if filter_response and filter_response[0]['InvoiceNumber']:
                    invoice.write({
                        'xero_exported': True,
                        'xero_invoice_no': filter_response[0]['InvoiceNumber'],
                        'xero_invoice_id': filter_response[0]['InvoiceID'],
                    })
                else:
                    invoice.write({
                        'xero_exported': True,
                        'xero_invoice_id': filter_response and filter_response[0]['InvoiceID'],
                    })
                self._cr.commit()
        self._cr.commit()


class account_tax(models.Model):
    """ Inherited to add new columns"""
    _inherit = 'account.tax'

    xero_tax_type = fields.Char('Xero Tax Type', size=64)
