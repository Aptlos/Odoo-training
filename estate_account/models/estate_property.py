from odoo import fields, models, Command


class EstatePropertyModel(models.Model):
    _inherit="estate.property"

    def action_do_sold(self):
        selling_price = self.selling_price
        admin_fee = 100000
        self.env['account.move'].create({
            'partner_id': self.buyer_id.id,  # партер - покупатель
            'move_type': 'out_invoice',  # тип
            'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id, # журнал продаж
            'invoice_line_ids': [
                Command.create({
                    'name': 'Commission (6%)',  # Description for this line
                    'quantity': 1,
                    'price_unit': selling_price * 0.94,
                }),
                Command.create({
                    'name': 'Administrative Fee',
                    'quantity': 1,
                    'price_unit': admin_fee,
                }),
            ]
        })
        return super().action_do_sold()