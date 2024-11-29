
from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Types"
    _sql_constraints = [
        ('check_type_name', 'UNIQUE(name)', 'Type name should be unique'),
    ]

    name=fields.Char(required=True)
    property_ids=fields.One2many('estate.property',
                                 'type_id','Properties')
    sequence=fields.Integer()
    _order = "sequence,name"

