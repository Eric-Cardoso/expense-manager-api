from flask import request
from functools import wraps
import jwt
import os

def login_required(f):
    @wraps(f)
    async def auth_logic(*args, **kwargs):
        try:
            auth_request = request.headers.get('Authorization')

            if not auth_request or not auth_request.startswith('Bearer '):
                return {'message_error': 'Operação inválida'}, 401

            decoded_token = jwt.decode(
                jwt=auth_request.split()[1], 
                key=os.getenv('SECRET_KEY'), 
                algorithms=[os.getenv('ALGORITHM')]
            )
        except Exception:
            return {'message_error': 'Operação inválida'}, 401

        call_func = await f(decoded_token, *args, **kwargs)

        return call_func  

    return auth_logic