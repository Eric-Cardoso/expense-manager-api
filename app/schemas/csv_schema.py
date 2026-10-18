from marshmallow import Schema, fields

from app.schemas.common_schema import flag_field, http_date_field

CSV_STATUS = ['pendente', 'processando', 'sucesso', 'erro']


class CsvUploadSchemaRequest(Schema):
    file = fields.Raw(
        required=True,
        metadata={
            'type': 'string',
            'format': 'binary',
            'description': 'Arquivo com extensão .csv'
        }
    )


class CsvSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    status = fields.String(metadata={'enum': CSV_STATUS})
    attached_at = http_date_field()
    valid = flag_field()


class CsvListSchemaResponse(Schema):
    success_message = fields.String()
    csvs = fields.List(fields.Nested(CsvSchema))


class CsvDetailSchemaResponse(Schema):
    success_message = fields.String()
    csv = fields.Nested(CsvSchema)