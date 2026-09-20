from flask import request
from app.repo.database import (
    get_connection,
    get_cursor,
    save_data,
    close_connection, 
    close_cursor
)
from app.repo.expense_repo import insert_expense, get_expenses, get_expense
from datetime import datetime


async def manually_enter_expense(request_token):
    db_conn = None
    db_cursor = None
    try:
        expense_data = request.get_json()

        if expense_data.get('csv_id'):
            raise ValueError(
                'This endpoint is only for manual expense entry'
            )

        if not expense_data.get('in_installments') and expense_data.get(
            'number_installments'
        ):
            raise ValueError(
                'Number of installments sent for a non-installment expense'
            )

        if expense_data.get('in_installments') and not expense_data.get(
            'number_installments'
        ):
            raise ValueError(
                'Number of installments is required for installment expenses'
            )

        if not expense_data.get('register_date') or not expense_data.get(
            'maturity_date'
        ):
            raise ValueError(
                'Register date and maturity date are required'
            )

        expense_data['user_id'] = int(request_token['sub'])

        try:
            expense_data['register_date'] = datetime.strptime(
                expense_data['register_date'], '%Y-%m-%d'
            )
            expense_data['maturity_date'] = datetime.strptime(
                expense_data['maturity_date'], '%Y-%m-%d'
            )
        except ValueError:
            raise ValueError(
                'Dates must be in the YYYY-MM-DD format'
            )

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        insert_expense(expense_data=expense_data, db_cursor=db_cursor)

        save_data(db_conn=db_conn)

        return {
            'success_message': 'Despesa registrada com sucesso'
        }, 201

    except Exception:
        if db_conn:
            db_conn.rollback()
        return {
            'error_message': (
                'Não foi possível registrar sua despesa, tente novamente'
            )
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)


async def get_user_expenses(request_token):
    db_conn = None
    db_cursor = None
    try:
        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        user_expenses = get_expenses(
            user_id=int(request_token['sub']),
            db_cursor=db_cursor
        )

        if not user_expenses:
            return {'error_message': 'Nenhuma despesa encontrada'}, 404

        return {
            'success_message': 'Despesas encontradas com sucesso',
            'expenses': user_expenses
        }, 200

    except Exception:
        return {
            'error_message': 'Erro ao buscar despesas, tente novamente'
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)


async def get_user_expense(request_token, header_expense_id):
    db_conn = None
    db_cursor = None
    try:
        if not header_expense_id:
            raise ValueError('Expense ID missing') 

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        user_expense = get_expense(
            expense_id=header_expense_id,
            logged_in_user_id=int(request_token['sub']),
            db_cursor=db_cursor
        )

        if not user_expense:
            return {'error_message': 'Despesa não encontrada'}, 404

        return {
            'success_message': 'Despesa encontrada com sucesso',
            'expense': user_expense
        }, 200

    except Exception:
        return {
            'error_message': 'Erro ao buscar despesa, tente novamente'
        }, 400

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)
