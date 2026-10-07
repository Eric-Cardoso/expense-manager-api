from app.repo.database import (
    get_connection,
    get_cursor,
    save_data,
    close_connection, 
    close_cursor
)
from app.repo.expense_repo import get_calc_expenses
from app.repo.report_repo import generate_report, get_reports, get_report
from datetime import datetime, timezone


async def generate_expenses_report(request_token) -> dict:
    db_conn = None
    db_cursor = None

    try:
        if not request_token:
            raise ValueError('request_token is required')

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_calc_expenses = get_calc_expenses(
            user_id=int(request_token['sub']), 
            db_cursor=db_cursor
        )

        if not db_calc_expenses:
            return {
                'error_message': (
                    'Não foi possível gerar o relatório, '
                    'nenhuma despesa encontrada'
                )
            }, 404

        generate_report(
            calc_expenses=db_calc_expenses,
            current_date=datetime.now(tz=timezone.utc).date(), 
            user_id=int(request_token['sub']), 
            db_cursor=db_cursor
        )

        save_data(db_conn=db_conn)

        return {
            'success_message': 'Relatório gerado com sucesso'
        }, 201
    
    except Exception:
        try:
            if db_conn:
                db_conn.rollback()
        except Exception:
            return {
                'error_message': (
                    'Não foi possível gerar o relatório, tente novamente'
                )
            }, 400 
        
        return {
            'error_message': (
                'Não foi possível gerar o relatório, tente novamente'
            )
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)


async def get_user_reports(request_token) -> list[dict]:
    db_conn = None
    db_cursor = None

    try:
        if not request_token:
            raise ValueError('request token is required')

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_reports = get_reports(
            user_id=int(request_token['sub']),
            db_cursor=db_cursor
        )

        if not db_reports:
            return {
                'error_message': (
                    'Não foi possível buscar os relatórios, '
                    'nenhum relatório encontrado'
                )
            }, 404

        return {
            'success_message': 'Relatórios buscados com sucesso',
            'reports': db_reports
        }, 200
    
    except Exception:
        return {
            'error_message': (
                'Não foi possível buscar os relatórios, tente novamente'
            )
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)


async def get_user_report(request_token, request_report_id: int) -> dict:
    db_conn = None
    db_cursor = None

    try:
        if not request_token or not request_report_id:
            raise ValueError('request token and request report id are required')

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        db_report = get_report(
            report_id=request_report_id,
            user_id=int(request_token['sub']),
            db_cursor=db_cursor
        )

        if not db_report:
            return {
                'error_message': (
                    'Não foi possível buscar o relatório, '
                    'relatório não encontrado'
                )
            }, 404

        return {
            'success_message': 'Relatório buscado com sucesso',
            'report': db_report
        }, 200

    except Exception:
        return {
            'error_message': (
                'Não foi possível buscar o relatório, tente novamente'
            )
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)