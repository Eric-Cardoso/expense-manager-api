from marshmallow import Schema, fields, validate

from app.schemas.common_schema import flag_field, http_date_field

EXPENSE_STATUS = ['pendente', 'pagando', 'quitado', 'atrasado']


class ExpenseSchemaRequest(Schema):
    title = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    category = fields.String(required=True, validate=validate.Length(max=50))
    status = fields.String(
        required=True, validate=validate.OneOf(EXPENSE_STATUS)
    )
    value = fields.Decimal(required=True, places=2)
    in_installments = fields.Boolean(required=True)
    number_installments = fields.Integer(
        allow_none=True,
        metadata={
            'description': (
                'Obrigatório se in_installments for true; '
                'proibido se for false'
            )
        }
    )
    register_date = fields.Date(
        required=True, metadata={'description': 'Formato YYYY-MM-DD'}
    )
    maturity_date = fields.Date(
        required=True, metadata={'description': 'Formato YYYY-MM-DD'}
    )


class ExpenseSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    csv_id = fields.Integer(allow_none=True)
    title = fields.String()
    description = fields.String(allow_none=True)
    category = fields.String()
    status = fields.String(metadata={'enum': EXPENSE_STATUS})
    value = fields.Decimal(as_string=True, places=2)
    in_installments = flag_field()
    number_installments = fields.Integer(allow_none=True)
    register_date = http_date_field()
    maturity_date = http_date_field()


class ExpenseListSchemaResponse(Schema):
    success_message = fields.String()
    expenses = fields.List(fields.Nested(ExpenseSchema))


class ExpenseDetailSchemaResponse(Schema):
    success_message = fields.String()
    expense = fields.Nested(ExpenseSchema)