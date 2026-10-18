from marshmallow import Schema, fields


class LoginSchemaRequest(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class LoginSchemaResponse(Schema):
    success_message = fields.String()
    token_type = fields.String(metadata={'example': 'Bearer'})
    access_token = fields.String()
    refresh_token = fields.String()


class RenewSessionSchemaRequest(Schema):
    refresh_token = fields.String(required=True)


class RenewSessionSchemaResponse(Schema):
    success_message = fields.String()
    access_token = fields.String()
    refresh_token = fields.String()