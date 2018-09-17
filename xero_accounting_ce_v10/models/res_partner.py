import ast
import json
import logging
from datetime import datetime

from odoo import fields, models, api
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char('XERO Reference', select=1, copy=False)

    @api.multi
    def _get_contact(self):
        partner_export_id = self._check_partner_exported()
        if partner_export_id:
            contact = {'ContactID': partner_export_id.xero_partner_id}
            return contact

    @api.multi
    def _check_partner_exported(self):
        company_id = self.env.user.company_id
        partner_export_id = self.env['exported.partner'].search([('company_id', '=', company_id.id), ('partner_id', '=', self.id),
                                                                 ('xero_update', '=', True)])
        partner_export_id = partner_export_id and partner_export_id[0]
        if not partner_export_id:
            partner_export_id = self._check_partner_exists_in_xero()
            if not partner_export_id:
                partner_export_id = self._export_partner()
        return partner_export_id

    @api.multi
    def _check_partner_exists_in_xero(self):
        company = self.env['res.users'].browse(self._uid).company_id
        if not company.consumer_key and not company.private_key_file:
            raise Warning('Please Set proper XERO credentials!')
        xero_client = company.get_xero_connection()
        try:
            response = xero_client.contacts.filter(AccountNumber=self.ref) or xero_client.contacts.filter(Name=self.name)
            if response:
                xero_partner_id = response[0].get('ContactID', False)
                self.write({'ref': response[0].get('AccountNumber')})
                exp_id = self.env['exported.partner'].create({
                    'company_id': company.id,
                    'partner_id': self.id,
                    'xero_partner_id': xero_partner_id,
                    'xero_update': True,
                })
                self._cr.commit()
                return exp_id
        except Exception as e:
            _logger.info(e)

        return False

    @api.multi
    def _export_partner(self):
        '''
        Exporting Partner to Xero
        '''
        company = self.env['res.users'].browse(self._uid).company_id

        account_number = self.env['ir.sequence'].next_by_code('res.partner.ref') or '00000'
        self.write({'ref': account_number})
        if not company.consumer_key and not company.private_key_file:
            raise Warning('Please Set proper XERO credentials!')
        exp_part_obj = self.env['exported.partner']
        xero_client = company.get_xero_connection()
        partner_currency, part_name = '', ''
        if self.property_product_pricelist:
            partner_currency = self.property_product_pricelist.currency_id.name
        if self.parent_id and self.parent_id.is_company:
            part_name = self.parent_id.name
        Contact_dic = {'Name': self.name or part_name,
                       'EmailAddress': self.email or '',
                       'FirstName': self.name,
                       'DefaultCurrency': partner_currency,
                       'Phones': {
                           'Phone': {'PhoneType': 'DEFAULT', 'PhoneNumber': self.phone or ''}
                       },
                       #                     'Website':self.website or '',
                       #                     'TaxNumber':self.abn or '',
                       'AccountNumber': account_number,
                       'IsSupplier': self.supplier and "true" or "false",
                       'IsCustomer': self.customer and "true" or "false",
                       'Addresses': {'Address': {
                           'AddressType': 'POBOX',
                           'AddressLine1': self.street or '',
                           'AddressLine2': self.street2 or '',
                           'AddressLine3': '',
                           'AddressLine4': '',
                           'City': self.city or '',
                           'Region': self.state_id and self.state_id.name or '',
                           'PostalCode': str(self.zip) or '',
                           'Country': self.country_id and self.country_id.name or ''}}
                       }
        Contact_dic = ast.literal_eval(json.dumps(Contact_dic))
        try:
            response = xero_client.contacts.put(Contact_dic)
            if self.phone:
                response[0].update({
                    'Phones': {
                        'Phone': {'PhoneType': 'DDI', 'PhoneNumber': self.phone or ''},
                    },
                })
            xero_client.contacts.save(response)
            if self.mobile:
                response[0].update({
                    'Phones': {
                        'Phone': {'PhoneType': 'MOBILE', 'PhoneNumber': self.mobile or ''},
                    },
                })
            xero_client.contacts.save(response)
            if self.fax:
                response[0].update({
                    'Phones': {
                        'Phone': {'PhoneType': 'FAX', 'PhoneNumber': self.fax or ''},
                    },
                })
            xero_client.contacts.save(response)
            self.env['xero.logs'].create({'name': 'Exported Partner %s! to Xero' % (self.name),
                                          'state': 'success',
                                          'partner_id': self.id,
                                          'date': datetime.now()})
            _logger.info('...Partner %s exported successfully to Xero...' % self.name)
        except Exception as e:
            _logger.info('\n\n e = = =', e)
            message = ''
            if e:
                for error in e.errors:
                    message += "\n" + error
            self.env['xero.logs'].create({'name': 'Unable to Export Partner %s! to Xero' % (self.name),
                                          'state': 'error',
                                          'partner_id': self.id,
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Unable to Export %s!\n%s' % (self.name, e))
        if response:
            xero_partner_id = response[0]['ContactID']
            exp_id = exp_part_obj.create({
                'company_id': company.id,
                'partner_id': self.id,
                'xero_partner_id': xero_partner_id,
                'xero_update': True,
            })
            self._cr.commit()

            # Sending Notification for Contact Creation
            template_id = self.env['ir.model.data'].get_object_reference('prag_xero_accounting_11', 'email_notify_contact_created')[1]
            email_template = self.env['mail.template'].browse(template_id)
            email_template.send_mail(res_id=exp_id.id, force_send=True)
            return exp_id

    @api.multi
    def write(self, vals):
        """ If Changes some fields of partner then set xero_update to False """
        ids = [rec.id for rec in self]
        if vals.get('name') or vals.get('email') or vals.get('property_product_pricelist') or vals.get('phone') or vals.get('street') \
                or vals.get('street2') or vals.get('city') or vals.get('state_id') or vals.get('zip') or vals.get('country_id'):
            exp_part_ids = self.env['exported.partner'].search([('partner_id', 'in', ids)])  # ('company_id', '=', company_id),
            if exp_part_ids:
                exp_part_ids.write({'xero_update': False})
        return super(res_partner, self).write(vals)


class exported_partner(models.Model):
    _name = "exported.partner"

    company_id = fields.Many2one('res.company', 'Company', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    xero_partner_id = fields.Char('Xero Partner Id', size=256, required=True)
    xero_update = fields.Boolean('Xero Update')


class PartnerUpdateDetailXero(models.TransientModel):
    _name = 'partner.update.detail.xero'

    @api.multi
    def update_partner_detail(self):
        company = self.env['res.users'].browse(self._uid).company_id
        exported = self.env['exported.partner']
        xero_client = company.get_xero_connection()
        for active_id in self._context['active_ids']:
            for part_id in self.env['res.partner'].browse(active_id):
                if part_id.ref:
                    try:
                        xero_part_id = exported.search([('partner_id', '=', part_id.id)])
                        if xero_part_id:
                            contacts_xero = xero_client.contacts.get(xero_part_id.xero_partner_id)
                            if contacts_xero:
                                contacts_xero[0].update({
                                    #                                    'TaxNumber':part_id.abn or '',
                                    'FirstName': part_id.name or '',
                                    'Name': part_id.name or '',
                                    'AccountNumber': part_id.ref or '',
                                    'Phones': {
                                        'Phone': {'PhoneType': 'DEFAULT', 'PhoneNumber': part_id.phone or ''},
                                    },
                                    'IsSupplier': part_id.supplier and "true" or "false",
                                    'IsCustomer': part_id.customer and "true" or "false",

                                    'Addresses': {'Address': {
                                        'AddressType': 'POBOX',
                                        'AddressLine1': part_id.street or '',
                                        'AddressLine2': part_id.street2 or '',
                                        'AddressLine3': '',
                                        'AddressLine4': '',
                                        'City': part_id.city or '',
                                        'Region': part_id.state_id and part_id.state_id.name or '',
                                        'PostalCode': str(part_id.zip) or '',
                                        'Country': part_id.country_id and part_id.country_id.name or ''}}
                                })
                                xero_client.contacts.save(contacts_xero)
                                contacts_xero[0].update({
                                    'Phones': {
                                        'Phone': {'PhoneType': 'MOBILE', 'PhoneNumber': part_id.mobile or ''},
                                    },
                                })
                                xero_client.contacts.save(contacts_xero)
                                contacts_xero[0].update({
                                    'Phones': {
                                        'Phone': {'PhoneType': 'FAX', 'PhoneNumber': part_id.fax or ''},
                                    },
                                })
                                xero_client.contacts.save(contacts_xero)
                                contacts_xero[0].update({
                                    'Phones': {
                                        'Phone': {'PhoneType': 'DDI', 'PhoneNumber': part_id.phone or ''}
                                    },
                                })
                                xero_client.contacts.save(contacts_xero)
                    except Exception as e:
                        raise Warning("Update Failed Due to:", e)
