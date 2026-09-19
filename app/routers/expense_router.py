from flask import Blueprint
from app.auth.decorators import login_required
from app.services.expense_service import (
    manually_enter_expense, 
    get_user_expenses
)


route_expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')


@route_expense_bp.route('/', methods=['POST'])
@login_required
async def route_manually_enter_expense(request_token) -> dict:
    return await manually_enter_expense(request_token=request_token)


@route_expense_bp.route('/', methods=['GET'])
@login_required
async def route_get_user_expenses(request_token) -> dict:
    return await get_user_expenses(request_token=request_token)

