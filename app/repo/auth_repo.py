from mysql.connector.abstracts import MySQLCursorAbstract

def insert_token_data(token_data: dict, db_cursor: MySQLCursorAbstract) -> None:
    insert_command = '''
        INSERT INTO refresh_tokens (
            user_id, token_hash, is_revoked, expiration_date, created_at
        )
        VALUES (%s, %s, %s, %s, %s)
    '''

    db_cursor.execute(insert_command, (
        token_data['user_id'],
        token_data['token_hash'],
        token_data['is_revoked'],
        token_data['expiration_date'], 
        token_data['created_at'],
    )) 

