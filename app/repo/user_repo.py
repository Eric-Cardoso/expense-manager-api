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



    