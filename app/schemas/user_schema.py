from marshmallow import Schema, fields, validate


class RegisterUserSchemaRequest(Schema):
    name = fields.String(validate=validate.Length(max=100))
    email = fields.Email(validate=validate.Length(max=80), required=True)
    password = fields.String(
        validate=validate.Length(min=8, max=72),
        required=True,
        load_only=True,
        metadata={
            'description': (
                'Mínimo de 8 caracteres, com maiúscula, número e '
                'caractere especial'
            )
        }
    )


class RegisterUserSchemaResponse(Schema):
    message_success = fields.String()


class RegisterUserSchemaErrorResponse(Schema):
    message_error = fields.String()