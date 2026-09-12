from dotenv import load_dotenv
from mysql.connector.abstracts import (
    MySQLConnectionAbstract, 
    MySQLCursorAbstract
)
import mysql.connector
import os

load_dotenv()

def get_connection() -> MySQLConnectionAbstract:
    return mysql.connector.connect(
        database=os.getenv('MYSQL_DATABASE'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('DATABASE_HOST'),
        port=int(os.getenv('DATABASE_PORT'))
    )

def get_cursor(db_conn: MySQLConnectionAbstract) -> MySQLCursorAbstract: 
    return db_conn.cursor()

def close_connection(db_conn: MySQLConnectionAbstract) -> None:
    db_conn.close()

def close_cursor(db_cursor: MySQLCursorAbstract) -> None:
    db_cursor.close()

def save_data(db_conn: MySQLConnectionAbstract) -> None:
    db_conn.commit()