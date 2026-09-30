from app.celery import celery_app
from app.repo.csv_repo import update_csv
from app.repo.database import (
    get_connection,
    get_cursor, 
    save_data,
    close_cursor,
    close_connection 
)
from app.repo.expense_repo import insert_expense_by_csv
from datetime import datetime
import csv


@celery_app.task
def process_csv(
    csv_path: str,
    csv_id: int,
    user_id: int
) -> None:

    db_conn = None
    db_cursor = None
    try:
    
        csv_info = {
            'csv_id': csv_id,
            'user_id': user_id,
            'status': 'processando'
        }

        db_conn = get_connection()
        db_cursor = get_cursor(db_conn=db_conn)

        update_csv(csv_info=csv_info, db_cursor=db_cursor)

        save_data(db_conn=db_conn)

        with open(file=csv_path, mode='r') as file:
            csv_data = list(csv.DictReader(file))

        if not csv_data:
            raise ValueError('CSV missing')

        for dict_row in csv_data:
            in_installments = (
                dict_row.get('in_installments', '')
                .strip()
                .lower() == 'true'
            )

            number_installments = dict_row.get('number_installments') or None
            if number_installments:
                try:
                    number_installments = int(number_installments)
                except (ValueError, TypeError):
                    raise ValueError(
                        'Number of installments must be a valid integer'
                    )
            
            if not in_installments and number_installments:
                raise ValueError(
                    'Number of installments sent for a non-installment expense'
                )

            if in_installments and not number_installments:
                raise ValueError(
                    'Number of installments is required for installment expenses'
                )

            if not dict_row.get('register_date') or not dict_row.get(
                'maturity_date'
            ):
                raise ValueError(
                    'Register date and maturity date are required'
                )

            try:
                dict_row['register_date'] = datetime.strptime(
                    dict_row['register_date'], '%Y-%m-%d'
                )
                dict_row['maturity_date'] = datetime.strptime(
                    dict_row['maturity_date'], '%Y-%m-%d'
                )
            except ValueError:
                raise ValueError(
                    'Dates must be in the YYYY-MM-DD format'
                )

            dict_row['csv_id'] = csv_id
            dict_row['user_id'] = user_id
            
            dict_row['in_installments'] = in_installments
            dict_row['number_installments'] = number_installments 
            
            try:
                dict_row['value'] = float(dict_row.get('value', ''))    
            except (ValueError, TypeError):
                raise ValueError('Value must be a valid number')

            insert_expense_by_csv(expense_data=dict_row, db_cursor=db_cursor)

        csv_info['status'] = 'sucesso'
        csv_info['valid'] = True

        update_csv(csv_info=csv_info, db_cursor=db_cursor)

        save_data(db_conn=db_conn)
    
    except Exception:
        if db_conn:
            db_conn.rollback()
        
        if db_cursor:
            csv_info['status'] = 'erro'
            update_csv(csv_info=csv_info, db_cursor=db_cursor)

        if db_conn:
            save_data(db_conn=db_conn)

    finally:
        if db_cursor:
            close_cursor(db_cursor=db_cursor)
        if db_conn:
            close_connection(db_conn=db_conn)

