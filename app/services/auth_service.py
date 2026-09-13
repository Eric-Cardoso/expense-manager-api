from flask import request
from app.auth.auth_user import (
    verify_password, 
    generate_access_token, 
    generate_refresh_token
)
from app.repo.database import (
    get_connection, 
    get_cursor, 
    close_connection, 
    close_cursor
)
from app.repo.user_repo import get_user_by_email
from dotenv import load_dotenv
import os

load_dotenv()


async def login_user() -> dict:
    db_conn = None
    db_cursor = None
    try:
        data_user = request.get_json()

        if not data_user['email'] or not data_user['password']:
            raise ValueError('Invalid arguments')

        db_conn = get_connection()

        db_cursor = get_cursor(db_conn=db_conn)

        db_user = get_user_by_email(
            user_email=data_user['email'], db_cursor=db_cursor
        )

        if not db_user:
            raise ValueError('User not found')

        verify_password(
            password_sent=data_user['password'], 
            user_password=db_user['password_hash']
        )

        access_token = generate_access_token(
            user_id=db_user['id'], 
            access_token_expiration_time=int(os.getenv(
                'ACCESS_TOKEN_EXPIRATION_TIME'
            ))
        )

        refresh_token = generate_refresh_token(
            user_id=db_user['id'],
            refresh_token_expiration_time=int(os.getenv(
                'REFRESH_TOKEN_EXPIRATION_TIME'
            ))
        )

        return {
            'success_message': 'Login realizado com sucesso',
            'token_type': 'Bearer',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200


    except Exception as error:
        print(error)
        return {
            'error_message': 'Não foi possível realizar o login, tente novamente'
        }, 401

    finally:
        if db_conn:
            close_connection(db_conn=db_conn)
        if db_cursor:
            close_cursor(db_cursor=db_cursor)



    