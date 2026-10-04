from mysql.connector.abstracts import MySQLCursorAbstract


def insert_csv(csv_data: dict, db_cursor: MySQLCursorAbstract) -> None:

    insert_command = '''
        INSERT INTO attached_csvs (user_id, status, attached_at, valid)
        VALUES (%s, %s, %s, %s)
    '''

    db_cursor.execute(insert_command, (
        csv_data['user_id'],
        csv_data['status'],
        csv_data['attached_at'],
        csv_data['valid']
    ))


def get_csvs(user_id: int, db_cursor: MySQLCursorAbstract) -> list[dict]:

    get_command = '''
        SELECT * FROM attached_csvs
        WHERE user_id = %s
    '''

    db_cursor.execute(get_command, (user_id,))

    return db_cursor.fetchall()


def get_csv(csv_id: int, user_id: int, db_cursor: MySQLCursorAbstract) -> dict:

    get_command = '''
        SELECT * FROM attached_csvs
        WHERE id = %s AND user_id = %s
    '''

    db_cursor.execute(get_command, (csv_id, user_id))

    return db_cursor.fetchone()


def update_csv(csv_info: dict, db_cursor: MySQLCursorAbstract) -> None:
    
    update_command = '''
        UPDATE attached_csvs
        SET 
            status = COALESCE(%s, status),
            valid = COALESCE(%s, valid)
        WHERE id = %s AND user_id = %s
    '''

    db_cursor.execute(update_command, (
        csv_info.get('status'),
        csv_info.get('valid'),
        csv_info['csv_id'],
        csv_info['user_id']
    ))