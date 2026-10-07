from datetime import date
from mysql.connector.abstracts import MySQLCursorAbstract

def generate_report(
    calc_expenses: dict, 
    current_date: date, 
    user_id: int, 
    db_cursor: MySQLCursorAbstract
) -> None:

    insert_command = '''
        INSERT INTO reports (
            user_id, 
            total_value, 
            total_expenses, 
            settled_expenses, 
            overdue_expenses, 
            created_at
        )
        VALUES (
            %s, 
            COALESCE(%s, 0), 
            COALESCE(%s, 0), 
            COALESCE(%s, 0), 
            COALESCE(%s, 0), 
            %s
        )
    '''

    db_cursor.execute(insert_command, (
        user_id,
        calc_expenses.get('total_value'), 
        calc_expenses.get('total_expenses'), 
        calc_expenses.get('settled_expenses'), 
        calc_expenses.get('overdue_expenses'),
        current_date
    ))


def get_reports(user_id: int, db_cursor: MySQLCursorAbstract) -> list[dict]:

    get_command = '''
        SELECT * FROM reports
        WHERE user_id = %s
    '''

    db_cursor.execute(get_command, (user_id,))

    return db_cursor.fetchall()
