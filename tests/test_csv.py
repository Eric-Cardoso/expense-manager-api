from datetime import datetime
from mysql.connector.errors import OperationalError, IntegrityError
from tasks.csv_tasks import process_csv

import pytest

@pytest.fixture
def expense():
    expense_data = {
        'title': 'Geladeira',
        'description': 'Comprei uma geladeira',
        'category': 'Eletrodoméstico',
        'status': 'pendente',
        'value': '2500',
        'in_installments': 'False',
        'register_date': '2008-02-12',
        'maturity_date': '2008-02-12'
    }

    return expense_data

@pytest.fixture
def mocker_token(mocker):
    token_data = {
        'sub': 1,
        'exp': mocker.ANY
    }

    return token_data

@pytest.fixture
def mocker_strptime(mocker):
    mocked_strptime = mocker.patch(
        'tasks.csv_tasks.datetime'
    )
    mocked_strptime.strptime.return_value = datetime(2008, 2, 12)

    return mocked_strptime.strptime

@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'tasks.csv_tasks.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'tasks.csv_tasks.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'tasks.csv_tasks.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'tasks.csv_tasks.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'tasks.csv_tasks.close_cursor'
    )

    return mocked_close_cursor

@pytest.fixture
def mocker_insert_expense_by_csv(mocker):
    mocked_insert_expense_by_csv = mocker.patch(
        'tasks.csv_tasks.insert_expense_by_csv'
    )

    return mocked_insert_expense_by_csv

@pytest.fixture
def mocker_csv_path():
    return {'csv_path': 'file.csv'}


@pytest.fixture
def mocker_csv_info():
    return {
        'csv_id': 1,
        'user_id': 1,
        'status': 'processando'
    }


@pytest.fixture
def mocker_csv_id():
    return 1


@pytest.fixture
def mocker_update_csv(mocker):
    mocked_update_csv = mocker.patch('tasks.csv_tasks.update_csv')

    return mocked_update_csv


@pytest.fixture
def mocker_csv(mocker):
    mocked_csv = mocker.patch('tasks.csv_tasks.csv')

    return mocked_csv

@pytest.fixture
def mocker_open(mocker):
    mocked_open = mocker.patch('tasks.csv_tasks.open')

    return mocked_open

async def test_process_csv_verify_expected_behavior(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv, 
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_strptime, mocker_csv_path,
    mocker_csv_id, mocker_csv_info, mocker_token, mocker_open
):
    # Arrange
    expense['register_date'] = mocker_strptime.return_value
    expense['maturity_date'] = mocker_strptime.return_value
    
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    expected_expense_data = {
        **expense,
        'csv_id': mocker_csv_id,
        'user_id': mocker_token['sub'],
        'in_installments': False,
        'number_installments': None,
        'value': float(expense['value']),
    }

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    
    mocker_csv_info['status'] = 'sucesso'
    mocker_csv_info['valid'] = True
    mocker_update_csv.assert_called_with(
        csv_info=mocker_csv_info,
        db_cursor=db_cursor
    )
    assert mocker_update_csv.call_count == 2
    
    mocker_save_data.assert_called_with(
        db_conn=db_conn
    )
    assert mocker_save_data.call_count == 2
    
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], 
        mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    
    mocker_strptime.assert_called_with(
        expense['register_date'],
        '%Y-%m-%d'
    )
    mocker_strptime.assert_called_with(
        expense['maturity_date'],
        '%Y-%m-%d'
    )
    assert mocker_strptime.call_count == 2
    
    mocker_insert_expense_by_csv.assert_called_once_with(
        expense_data=expected_expense_data, 
        db_cursor=db_cursor
    )
    db_conn.rollback.assert_not_called()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


async def test_process_csv_should_raise_exception_if_connection_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    db_conn = mocker_get_connection.return_value
    mocker_get_connection.side_effect = OperationalError('Connection lost')

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_not_called()
    mocker_update_csv.assert_not_called()
    db_conn.rollback.assert_not_called()
    mocker_save_data.assert_not_called()
    mocker_open.assert_not_called()
    mocker_csv.DictReader.assert_not_called()
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    mocker_close_cursor.assert_not_called()
    mocker_close_connection.assert_not_called()


async def test_process_csv_should_raise_exception_if_cursor_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    db_conn = mocker_get_connection.return_value
    mocker_get_cursor.side_effect = OperationalError('Cursor lost')

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_update_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    mocker_save_data.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_not_called()
    mocker_csv.DictReader.assert_not_called()
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    mocker_close_cursor.assert_not_called()
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_csv_missing(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = []

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()

    mocker_update_csv.assert_called_with(
        csv_info={
            'csv_id': mocker_csv_id,
            'user_id': mocker_token['sub'],
            'status': 'erro'
        },
        db_cursor=db_cursor
    )
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_number_installments_invalid(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['in_installments'] = 'True'
    expense['number_installments'] = 'abc'

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_number_installments_sent_for_non_installment(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['in_installments'] = 'False'
    expense['number_installments'] = '3'

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_number_installments_required(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['in_installments'] = 'True'
    expense['number_installments'] = ''

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_dates_missing(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['register_date'] = ''

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_not_called()
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_dates_invalid_format(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    mocker_strptime.side_effect = ValueError('time data does not match format')

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_called_once_with(
        expense['register_date'], '%Y-%m-%d'
    )
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_value_invalid(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['register_date'] = mocker_strptime.return_value
    expense['maturity_date'] = mocker_strptime.return_value
    expense['value'] = 'não é número'

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_called_with(
        expense['register_date'], '%Y-%m-%d'
    )
    mocker_strptime.assert_called_with(
        expense['maturity_date'], '%Y-%m-%d'
    )
    assert mocker_strptime.call_count == 2
    mocker_insert_expense_by_csv.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_process_csv_should_raise_exception_if_insert_expense_by_csv_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_csv,
    mocker_close_connection, mocker_close_cursor, mocker_update_csv, expense,
    mocker_insert_expense_by_csv, mocker_csv_path, mocker_csv_id, mocker_token,
    mocker_open, mocker_strptime
):
    # Arrange
    expense['register_date'] = mocker_strptime.return_value
    expense['maturity_date'] = mocker_strptime.return_value

    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_csv.DictReader.return_value = [expense]
    mocker_insert_expense_by_csv.side_effect = IntegrityError(
        'Constraint violation'
    )

    # Act
    process_csv(
        csv_path=mocker_csv_path['csv_path'],
        csv_id=mocker_csv_id,
        user_id=mocker_token['sub']
    )

    # Assert
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
    mocker_open.assert_called_once_with(
        file=mocker_csv_path['csv_path'], mode='r'
    )
    mocker_csv.DictReader.assert_called_once_with(
        mocker_open.return_value.__enter__.return_value
    )
    mocker_strptime.assert_called_with(
        expense['register_date'], '%Y-%m-%d'
    )
    mocker_strptime.assert_called_with(
        expense['maturity_date'], '%Y-%m-%d'
    )
    assert mocker_strptime.call_count == 2
    mocker_insert_expense_by_csv.assert_called_once_with(
        expense_data=expense,
        db_cursor=db_cursor
    )
    db_conn.rollback.assert_called_once()
    assert mocker_update_csv.call_count == 2
    assert mocker_save_data.call_count == 2
    mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
    mocker_close_connection.assert_called_once_with(db_conn=db_conn)