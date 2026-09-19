from app.services.expense_service import manually_enter_expense
from mysql.connector.errors import OperationalError, IntegrityError
from datetime import datetime
import pytest



@pytest.fixture
def expense():
    expense_data = {
        'title': 'Geladeira',
        'description': 'Comprei uma geladeira',
        'category': 'Eletrodoméstico',
        'status': 'pendente',
        'value': 2500,
        'in_installments': False,
        'register_date': '2008-02-12',
        'maturity_date': '2008-02-12'
    }

    return expense_data

@pytest.fixture
def mocker_request_token():
    request_token_data = {
        'sub': 1,
    }

    return request_token_data

@pytest.fixture
def mocker_strptime(mocker):
    mocked_strptime = mocker.patch(
        'app.services.expense_service.datetime'
    )
    mocked_strptime.strptime.return_value = datetime(2008, 2, 12)

    return mocked_strptime.strptime

@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'app.services.expense_service.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'app.services.expense_service.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'app.services.expense_service.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'app.services.expense_service.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'app.services.expense_service.close_cursor'
    )

    return mocked_close_cursor

@pytest.fixture
def mocker_insert_expense(mocker):
    mocked_insert_expense = mocker.patch(
        'app.services.expense_service.insert_expense'
    )

    return mocked_insert_expense


async def test_register_expense_verify_expected_behavior(
    expense, mocker_get_connection, mocker_get_cursor, mocker_save_data, app, 
    mocker_close_connection, mocker_close_cursor, mocker_insert_expense, 
    mocker_request_token, mocker_strptime
) -> None:

    with app.test_request_context(json=expense):
        # Arrange
        expense['user_id'] = mocker_request_token['sub']
        expense['register_date'] = mocker_strptime.return_value
        expense['maturity_date'] = mocker_strptime.return_value

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        expected_success_message = 'Despesa registrada com sucesso'

        # Act
        response, status_code = await manually_enter_expense(
            request_token=mocker_request_token
        )

        # Assert
        assert expected_success_message == response['success_message']
        assert status_code == 201

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_insert_expense.assert_called_once_with(
            expense_data=expense,
            db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(
            db_conn=db_conn
        )
        db_conn.rollback.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )


async def test_register_expense_should_raise_exception_if_connection_fails(
    expense, mocker_get_connection, mocker_get_cursor, mocker_save_data, app, 
    mocker_close_connection, mocker_close_cursor, mocker_insert_expense,
    mocker_request_token
) -> None:

    with app.test_request_context(json=expense):

        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_error_message = (
            'Não foi possível registrar sua despesa, tente novamente'
        )

        # Act
        response, status_code = await manually_enter_expense(
            request_token=mocker_request_token
        )

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_insert_expense.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_get_connection.return_value.rollback.assert_not_called()
        mocker_close_cursor.assert_not_called() 
        mocker_close_connection.assert_not_called()


async def test_register_expense_should_raise_exception_if_cursor_fails(
    expense, mocker_get_connection, mocker_get_cursor, mocker_save_data, app, 
    mocker_close_connection, mocker_close_cursor, mocker_insert_expense,
    mocker_request_token
) -> None:

    with app.test_request_context(json=expense):

        # Arrange
        db_conn = mocker_get_connection.return_value
        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_error_message = (
            'Não foi possível registrar sua despesa, tente novamente'
        )

        # Act
        response, status_code = await manually_enter_expense(
            request_token=mocker_request_token
        )

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_insert_expense.assert_not_called()
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_register_expense_should_raise_exception_if_insert_expense_fails(
    expense, mocker_get_connection, mocker_get_cursor, mocker_save_data, app, 
    mocker_close_connection, mocker_close_cursor, mocker_insert_expense,
    mocker_request_token, mocker_strptime
) -> None:

    with app.test_request_context(json=expense):

        # Arrange
        expense['user_id'] = mocker_request_token['sub']
        expense['register_date'] = mocker_strptime.return_value
        expense['maturity_date'] = mocker_strptime.return_value

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_insert_expense.side_effect = IntegrityError(
            'Constraint violation'
        )

        expected_error_message = (
            'Não foi possível registrar sua despesa, tente novamente'
        )

        # Act
        response, status_code = await manually_enter_expense(
            request_token=mocker_request_token
        )

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_insert_expense.assert_called_once_with(
            expense_data=expense,
            db_cursor=db_cursor
        )
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_register_expense_should_raise_exception_if_save_data_fails(
    expense, mocker_get_connection, mocker_get_cursor, mocker_save_data, app, 
    mocker_close_connection, mocker_close_cursor, mocker_insert_expense,
    mocker_request_token, mocker_strptime
) -> None:

    with app.test_request_context(json=expense):

        # Arrange
        expense['user_id'] = mocker_request_token['sub']
        expense['register_date'] = mocker_strptime.return_value
        expense['maturity_date'] = mocker_strptime.return_value

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_save_data.side_effect = OperationalError('Connection lost')

        expected_error_message = (
            'Não foi possível registrar sua despesa, tente novamente'
        )

        # Act
        response, status_code = await manually_enter_expense(
            request_token=mocker_request_token
        )

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_insert_expense.assert_called_once_with(
            expense_data=expense,
            db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(
            db_conn=db_conn
        )
        db_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )