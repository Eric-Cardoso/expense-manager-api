from mysql.connector.abstracts import MySQLCursorAbstract

def insert_expense(expense_data: dict, db_cursor: MySQLCursorAbstract) -> None:
    insert_command = '''
        INSERT INTO expenses (
            user_id,
            csv_id,
            title,
            description,
            category,
            status,
            value,
            in_installments,
            number_installments,
            register_date,
            maturity_date
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    db_cursor.execute(insert_command, (
        expense_data['user_id'],
        None,
        expense_data['title'],
        expense_data['description'],
        expense_data['category'],
        expense_data['status'],
        expense_data['value'],
        expense_data['in_installments'],
        expense_data.get('number_installments'),
        expense_data['register_date'],
        expense_data['maturity_date']
    ))


def get_expenses(user_id: int, db_cursor: MySQLCursorAbstract) -> list[dict]:
    get_expenses_command = '''
        SELECT * FROM expenses
        WHERE user_id = %s
    '''

    db_cursor.execute(get_expenses_command, (user_id,))

    return db_cursor.fetchall()