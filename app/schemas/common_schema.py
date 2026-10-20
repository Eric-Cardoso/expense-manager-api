from marshmallow import Schema, fields


class MessageResponseSchema(Schema):
    success_message = fields.String()


class ErrorResponseSchema(Schema):
    error_message = fields.String()


def http_date_field() -> fields.String:
    return fields.String(
        metadata={
            'description': ('Data no formato HTTP (serialização padrão do Flask)'),
            'example': 'Sun, 18 Oct 2026 00:00:00 GMT',
        }
    )


def flag_field() -> fields.Integer:
    return fields.Integer(metadata={'description': '0 = não, 1 = sim'})
