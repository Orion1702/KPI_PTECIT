from marshmallow import Schema, fields


class GpsSchema(Schema):
    longitude = fields.Float() # Заміна Number на Float
    latitude = fields.Float() # Заміна Number на Float
