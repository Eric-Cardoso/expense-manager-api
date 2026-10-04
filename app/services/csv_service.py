from app.repo.csv_repo import get_csvs, get_csv
from app.repo.database import (
    get_connection,
    get_cursor,
    close_connection, 
    close_cursor
)


async def get_user_csvs(request_token) -> dict:
    db_conn = None
    db_cursor = None

    try:

        if not request_token:
            raise ValueError('request token is required')

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_csvs = get_csvs(
            user_id=int(request_token['sub']), 
            db_cursor=db_cursor
        )

        if not db_csvs:
            return {
                'error_message': (
                    'Não foi possível listar os CSVs, nenhum CSV encontrado'
                )
            }, 404

        return {
            'success_message': 'CSVs buscados com sucesso',
            'csvs': db_csvs
        }, 200
        

    except Exception:
        return {
            'error_message': 'Não foi possível listar os CSVs, tente novamente'
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)


async def get_user_csv(request_token, request_csv_id) -> dict:
    db_conn = None
    db_cursor = None
    
    try:

        if not request_token or not request_csv_id:
            raise ValueError('request token and request_csv_id are required')

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_csv = get_csv(
            csv_id=request_csv_id, 
            user_id=int(request_token['sub']), 
            db_cursor=db_cursor
        )

        if not db_csv:
            return {
                'error_message': (
                    'Não foi possível listar o CSV, CSV não encontrado'
                )
            }, 404

        return {
            'success_message': 'CSV buscado com sucesso',
            'csv': db_csv
        }, 200

    except Exception:
        return {
            'error_message': 'Não foi possível listar o CSV, tente novamente'
        }, 400

    finally:   
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)