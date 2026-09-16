from flask import Blueprint
from app.services.user_service import register_user

route_user_bp = Blueprint('user', __name__, url_prefix='/users')

@route_user_bp.route('/', methods=['POST'])
async def route_register_user() -> dict:
    return await register_user()