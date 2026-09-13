from mysql.connector.abstracts import MySQLCursorAbstract

def insert_user(data_user: dict, db_cursor: MySQLCursorAbstract) -> None:

    insert_comand = '''
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
    '''

    db_cursor.execute(insert_comand, (
        data_user['name'], 
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

    



    