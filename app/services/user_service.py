from app.auth.auth_user import (
    validate_user_email, 
    validate_user_password, 
    encrypt_password
)
from flask import request
from app.repo.database import (
    get_connection,
    get_cursor,
    close_connection, 
    close_cursor, 
    save_data
)
from app.repo.user_repo import insert_user

async def register_user() -> dict:
    db_conn = None
    db_cursor = None
    try:
        data_user = request.get_json()

        if not data_user['email'] or not data_user['password']:
            raise ValueError('Invalid credentials')

        validate_user_email(user_email=data_user['email'])

        validate_user_password(user_password=data_user['password'])

        data_user['password'] = encrypt_password(
            user_password=data_user['password']
        )

        db_conn = get_connection()
        
        db_cursor = get_cursor(db_conn=db_conn)

        insert_user(data_user=data_user, db_cursor=db_cursor)

        save_data(db_conn=db_conn)

        return {'message_success': 'Usuário cadastrado com sucesso'}, 201

    except Exception:
        if db_conn:
            try:
                db_conn.rollback()
            except Exception:
                return {
                    'message_error': 'Erro ao finalizar cadastro, tente novamente'
                }, 400
        return {'message_error': 'Erro ao finalizar cadastro, tente novamente'}, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)