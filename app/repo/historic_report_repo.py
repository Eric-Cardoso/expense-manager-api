from datetime import datetime

from mysql.connector.abstracts import MySQLCursorAbstract


def get_historic_reports_data(
    initial_date_month: datetime,
    final_date_month: datetime,
    db_cursor: MySQLCursorAbstract,
) -> list[dict]:

    get_command = '''
        SELECT
            user_id,
            SUM(value) AS spent_value,
            COUNT(id) AS spent_expenses,
            COUNT(IF(status = %s, id, NULL)) AS settled_expenses,
            COUNT(IF(status = %s, id, NULL)) AS overdue_expenses
        FROM expenses
        WHERE maturity_date >= %s AND maturity_date <= %s
        GROUP BY user_id
    '''

    db_cursor.execute(
        get_command, ('quitado', 'atrasado', initial_date_month, final_date_month)
    )

    return db_cursor.fetchall()


def generate_historic_reports(
    reports_data: dict, db_cursor: MySQLCursorAbstract
) -> None:

    insert_command = '''
        INSERT INTO historic_reports (
            user_id,
            month_report,
            spent_value,
            spent_expenses,
            settled_expenses,
            overdue_expenses,
            generated_at
        )
        VALUES (
            %s,
            %s,
            COALESCE(%s, 0),
            COALESCE(%s, 0),
            COALESCE(%s, 0),
            COALESCE(%s, 0),
            %s
        )
    '''

    db_cursor.execute(
        insert_command,
        (
            reports_data.get('user_id'),
            reports_data.get('month_report'),
            reports_data.get('spent_value'),
            reports_data.get('spent_expenses'),
            reports_data.get('settled_expenses'),
            reports_data.get('overdue_expenses'),
            reports_data.get('generated_at'),
        ),
    )


def get_historic_reports(user_id: int, db_cursor: MySQLCursorAbstract) -> list[dict]:

    get_command = '''
        SELECT * FROM historic_reports
        WHERE user_id = %s
    '''

    db_cursor.execute(get_command, (user_id,))

    return db_cursor.fetchall()


def get_historic_report(
    historic_report_id: int, user_id: int, db_cursor: MySQLCursorAbstract
) -> dict:

    get_command = '''
        SELECT * FROM historic_reports
        WHERE id = %s AND user_id = %s
    '''

    db_cursor.execute(get_command, (historic_report_id, user_id))

    return db_cursor.fetchone()


def delete_historic_report(
    historic_report_id: int, user_id: int, db_cursor: MySQLCursorAbstract
) -> None:

    delete_command = '''
        DELETE FROM historic_reports
        WHERE id = %s AND user_id = %s
    '''

    db_cursor.execute(delete_command, (historic_report_id, user_id))
