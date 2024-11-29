from datetime import timedelta

from odoo import api,fields, models
from odoo.exceptions import UserError
from odoo.fields import One2many


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    _sql_constraints = [
        ('check_expected_price','CHECK ( expected_price>0 )','Expected price should be strictly positive'),
        ('check_selling_price','CHECK ( selling_price>=0 )','Selling price should be positive'),
    ]

    tag_ids = fields.Many2many('estate.property.tag',string='Tags')
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    type_id = fields.Many2one('estate.property.type',string='Property Type')
    date_availability = fields.Date(copy=False,default=fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean(default=True)
    garden_area = fields.Integer(default=10)
    total_area = fields.Float(compute="_compute_total")

    salesperson_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=True,
                              default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one(
        'res.partner', string='Buyer',
                    index=True, tracking=True,copy=False
    )

    garden_orientation = fields.Selection(
        string='Orientation',selection=[
            ('north','North'),
            ('south','South'),
            ('east','East'),
            ('west','West')
        ],
        default='north')

    state = fields.Selection(
        string='State of property',selection=[
            ('new','New'),
            ('offer_received','Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'),
            ('canceled','Canceled')
        ],
        default='new',required=True, copy=False)

    offer_ids = fields.One2many(
        'estate.property.offer','property_id','Offers'
    )
    best_price = fields.Float(compute="_compute_best_price")

    #Compute methods
    @api.depends('living_area','garden_area')
    def _compute_total(self):
        for record in self:
            record.total_area=record.living_area+record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            if len(record.offer_ids)!=0:
                record.best_price=max(record.offer_ids.mapped('price'))
            else:
                record.best_price=0

    #Constraints and onchange
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.buyer_id !='':
                if record.selling_price<record.expected_price*0.9:
                    raise UserError('Selling price shouldnt be lower than 90% of expected price')


    @api.onchange('garden')
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area=0
            self.garden_orientation=''
        if self.garden:
            self.garden_area=10
            self.garden_orientation='north'

    #CRUD
    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_new(self):
        if not set(self.mapped('state')) & {'new', 'canceled'}:
            raise UserError('Cant delete not new or canceled properties')


    #Actions
    def action_do_sold(self):
        for record in self:
            if record.state!= 'canceled':
                record.state='sold'
            else:
                raise UserError('Already canceled')
        return True

    def action_do_canceled(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
            else:
                raise UserError('Already sold')
        return True