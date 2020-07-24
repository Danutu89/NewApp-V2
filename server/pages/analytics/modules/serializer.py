from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema
from models import Location, Ip_Location, View
from app import db

class LocationSchema(ModelSchema):
    class Meta:
        model = Location
        sqla_session = db.session

class IpSchema(ModelSchema):
    location = fields.Nested(LocationSchema, many=False)

    class Meta:
        model = Ip_Location
        sqla_session = db.session
        include_fk = True
        

class ViewSchema(ModelSchema):
    ip = fields.Nested(IpSchema, many=False)

    class Meta:
        model = View
        sqla_session = db.session
        include_fk = True
        