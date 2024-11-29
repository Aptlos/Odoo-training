from datetime import timedelta

from odoo import api,fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offers"
    _sql_constraints = [
        ('check_price', 'CHECK ( price>=0 )', 'Price should be strictly positive'),
    ]

    create_date = fields.Date(readonly=True, default=fields.Datetime.now)
    price=fields.Float()
    status=fields.Selection(
        string='Status',
        selection=[
            ('accepted','Accepted'),
            ('refused','Refused')
        ],
        copy=False, readonly=True)
    partner_id=fields.Many2one('res.partner',string='Partner')
    property_id=fields.Many2one('estate.property',string='Property')
    validity=fields.Integer(default=7)
    date_deadline=fields.Date(compute='_compute_deadline', inverse='_inverse_deadline')
    _order = "price desc"

    #Compute methods
    @api.depends('validity','create_date')
    def _compute_deadline(self):
        for record in self:
            record.date_deadline=record.create_date+timedelta(days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            record.validity=(record.date_deadline-record.create_date).days

    #CRUD
    @api.model
    def create(self, vals):
        if vals['price']<self.env['estate.property'].browse(vals['property_id']).best_price:
            raise UserError('There is offer with better price')
        self.env['estate.property'].browse(vals['property_id']).state='offer_received'
        return super().create(vals)

    #Actions
    def action_cancel(self):
        for record in self:
            if record.status=='accepted':
                record.property_id.selling_price = 0
                record.property_id.buyer_id = ''
            record.status='refused'
        return True

    def action_confirm(self):
        for record in self:
            if record.property_id.selling_price ==0:
                record.status='accepted'
                record.property_id.selling_price=record.price
                record.property_id.buyer_id=record.partner_id
                record.property_id.state='offer_accepted'
            else:
                continue

        return True