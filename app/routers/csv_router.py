from flask import Blueprint
from app.auth.decorators import login_required
from app.services.csv_service import get_user_csvs


route_csv_bp = Blueprint('csv', __name__, url_prefix='/csvs')

@route_csv_bp.route('/', methods=['GET'])
@login_required
async def route_get_user_csvs(request_token) -> list[dict]:
    return await get_user_csvs(request_token=request_token)