from flask import request
from app.auth.auth_user import (
    verify_password, 
    generate_access_token, 
    generate_refresh_token
)
from app.repo.database import (
    get_connection, 
    get_cursor,
    save_data, 
    close_connection, 
    close_cursor
)
from app.repo.auth_repo import insert_token_data
from app.repo.user_repo import get_user_by_email
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import hashlib
import os


load_dotenv()


async def login_user() -> dict:
    db_conn = None
    db_cursor = None
    try:
        data_user = request.get_json()

        if not data_user['email'] or not data_user['password']:
            raise ValueError('Invalid arguments')

        refresh_token_expiration_date = datetime.now(timezone.utc) + timedelta(
            days=int(os.getenv('REFRESH_TOKEN_EXPIRATION_TIME'))
        )

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
            access_token_expiration_time=int(
                os.getenv('ACCESS_TOKEN_EXPIRATION_TIME')
            )
        )

        refresh_token = generate_refresh_token(
            user_id=db_user['id'],
            refresh_token_expiration_time=int(
                os.getenv('REFRESH_TOKEN_EXPIRATION_TIME')
            )
        )

        token_bytes = refresh_token.encode('utf-8')

        hashed_token = hashlib.sha256(token_bytes).hexdigest()

        token_data = {
            'user_id': db_user['id'],
            'token_hash': hashed_token,
            'is_revoked': False,
            'expiration_date': refresh_token_expiration_date,
            'created_at': datetime.now(timezone.utc)
        }

        insert_token_data(token_data=token_data, db_cursor=db_cursor)

        save_data(db_conn=db_conn)

        return {
            'success_message': 'Login realizado com sucesso',
            'token_type': 'Bearer',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200


    except Exception:
        return {
            'error_message': 'Não foi possível realizar o login, tente novamente'
        }, 401

    finally:
        if db_conn:
            close_connection(db_conn=db_conn)
        if db_cursor:
            close_cursor(db_cursor=db_cursor)



    