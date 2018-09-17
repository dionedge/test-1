from datetime import datetime

from odoo import models, fields
from odoo.exceptions import Warning
from xero import Xero
from xero.auth import PrivateCredentials


class res_company(models.Model):
    _inherit = "res.company"

    consumer_key = fields.Char('CONSUMER KEY', size=256)
    private_key_file = fields.Char('PATH TO PRIVATE KEY FILE (.pem file)', size=256)

    def get_xero_connection(self):
        """ this method will set connection between xero to odoo """
        if self.consumer_key and self.private_key_file:
            with open(self.private_key_file) as keyfile:
                rsa_key = keyfile.read()
            credential = PrivateCredentials(self.consumer_key, rsa_key)
            unit_price_4dps = True
            xero = Xero(credential, unit_price_4dps)
            return xero
        else:
            self.env['xero.logs'].create({'name': 'Consumer Key And Private Key File Not Define Properly for Company %s' % (self.name),
                                          'state': 'error',
                                          'date': datetime.now()})
            self._cr.commit()
            raise Warning('Consumer Key And Private Key File Not Define Properly for Company %s' % (self.name))
