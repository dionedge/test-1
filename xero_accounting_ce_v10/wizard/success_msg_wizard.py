from odoo import models, fields, api


class export_success_msg(models.TransientModel):
    _name = 'export.success.msg'
    _description = 'Will show if all invoices are exported successfully'

    success_msg_id = fields.Char("Invoice Exported Successfully!!")

    @api.multi
    def ok_msg(self):
        return {
            'type': 'ir.actions.act_window_close',
        }
