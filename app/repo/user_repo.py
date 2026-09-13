from mysql.connector.abstracts import MySQLCursorAbstract

def insert_user(data_user: dict, db_cursor: MySQLCursorAbstract) -> None:

    insert_command = '''
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
    '''

    db_cursor.execute(insert_command, (
        data_user['name'] if data_user.get('name') else None, 
        data_user['email'], 
        data_user['password']
    ))


def get_user_by_email(
    user_email: str, db_cursor: MySQLCursorAbstract
) -> dict | None:

    select_comand = '''
        SELECT id, name, email, password_hash
        FROM users
        WHERE email = %s
    '''

    db_cursor.execute(select_comand, (user_email,))

    return db_cursor.fetchone()

    



    