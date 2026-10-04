from flask import Blueprint
from app.auth.decorators import login_required
from app.services.csv_service import (
    get_user_csvs, 
    get_user_csv, 
    delete_user_csv
)


route_csv_bp = Blueprint('csv', __name__, url_prefix='/csvs')

@route_csv_bp.route('/', methods=['GET'])
@login_required
async def route_get_user_csvs(request_token) -> list[dict]:
    return await get_user_csvs(request_token=request_token)


@route_csv_bp.route('/<int:request_csv_id>', methods=['GET'])
@login_required
async def route_get_user_csv(request_token, request_csv_id) -> dict:
    return await get_user_csv(
        request_token=request_token, 
        request_csv_id=request_csv_id
    )


@route_csv_bp.route('/<int:request_csv_id>', methods=['DELETE'])
@login_required
async def route_delete_user_csv(request_token, request_csv_id) -> None:
    return await delete_user_csv(
        request_token=request_token, 
        request_csv_id=request_csv_id
    )