
from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tags"
    _sql_constraints = [
        ('check_tag_name', 'UNIQUE(name)', 'Tag name should be unique'),
    ]

    name=fields.Char(required=True)
    color=fields.Integer()
    _order = "name"

