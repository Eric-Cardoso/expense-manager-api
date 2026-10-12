from app.services.historic_report_service import (
    generate_user_historic_reports, 
    get_user_historic_reports, 
    get_user_historic_report,
    delete_user_historic_report
)
from datetime import timezone, datetime
from mysql.connector.errors import OperationalError, IntegrityError
import pytest


@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'app.services.historic_report_service.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'app.services.historic_report_service.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'app.services.historic_report_service.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'app.services.historic_report_service.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'app.services.historic_report_service.close_cursor'
    )

    return mocked_close_cursor

@pytest.fixture
def current_datetime():
    return datetime(2026, 10, 6, 0, 0, 0, tzinfo=timezone.utc)

@pytest.fixture
def mocker_datetime(mocker, current_datetime):
    mocked_datetime = mocker.patch(
        'app.services.historic_report_service.datetime'
    )
    mocked_datetime.now.return_value = current_datetime

    return mocked_datetime

@pytest.fixture
def initial_date_month():
    return datetime(2026, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

@pytest.fixture
def final_date_month():
    return datetime(2026, 9, 30, 23, 59, 59, 999999, tzinfo=timezone.utc)

@pytest.fixture
def reports_data():
    return [
        {
            'id': 1,
            'user_id': 1,
            'spent_value': 200,
            'spent_expenses': 3,
            'settled_expenses': 5,
            'overdue_expenses': 3
        },
        {
            'id': 2,
            'user_id': 2,
            'spent_value': 432,
            'spent_expenses': 7,
            'settled_expenses': 0,
            'overdue_expenses': 2
        }
    ]

@pytest.fixture
def expected_reports_data(current_datetime):
    return [
        {
            'id': 1,
            'user_id': 1,
            'spent_value': 200,
            'spent_expenses': 3,
            'settled_expenses': 5,
            'overdue_expenses': 3,
            'month_report': '2026-09-30',
            'generated_at': current_datetime
        },
        {
            'id': 2,
            'user_id': 2,
            'spent_value': 432,
            'spent_expenses': 7,
            'settled_expenses': 0,
            'overdue_expenses': 2,
            'month_report': '2026-09-30',
            'generated_at': current_datetime
        }
    ]

@pytest.fixture
def mocker_get_historic_reports_data(mocker):
    mocked_get_historic_reports_data = mocker.patch(
        'app.services.historic_report_service.get_historic_reports_data'
    )

    return mocked_get_historic_reports_data

@pytest.fixture
def mocker_generate_historic_reports(mocker):
    mocked_generate_historic_reports = mocker.patch(
        'app.services.historic_report_service.generate_historic_reports'
    )

    return mocked_generate_historic_reports

@pytest.fixture
def mocker_print_exc(mocker):
    mocked_print_exc = mocker.patch(
        'app.services.historic_report_service.print_exc'
    )

    return mocked_print_exc

@pytest.fixture
def mocker_token(mocker):
    token_data = {
        'sub': 1,
        'exp': mocker.ANY
    }

    return token_data

@pytest.fixture
def mocker_get_historic_reports(mocker):
    mocked_get_historic_reports = mocker.patch(
        'app.services.historic_report_service.get_historic_reports'
    )

    return mocked_get_historic_reports

@pytest.fixture
def mocker_historic_report_id():
    return 1

@pytest.fixture
def mocker_get_historic_report(mocker):
    mocked_get_historic_report = mocker.patch(
        'app.services.historic_report_service.get_historic_report'
    )

    return mocked_get_historic_report

@pytest.fixture
def mocker_delete_historic_report(mocker):
    mocked_delete_historic_report = mocker.patch(
        'app.services.historic_report_service.delete_historic_report'
    )

    return mocked_delete_historic_report


def test_generate_user_historic_reports_verify_expected_behavior(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month, reports_data, expected_reports_data
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.return_value = reports_data

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    assert mocker_generate_historic_reports.call_count == 2
    mocker_generate_historic_reports.assert_any_call(
        reports_data=expected_reports_data[0],
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_called_with(
        reports_data=expected_reports_data[1],
        db_cursor=db_cursor
    )
    assert mocker_save_data.call_count == 2
    mocker_save_data.assert_called_with(
        db_conn=db_conn
    )
    db_conn.rollback.assert_not_called()
    mocker_print_exc.assert_not_called()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_raise_exception_if_datetime_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports
) -> None:

    # Arrange
    mocker_datetime.now.side_effect = Exception

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_not_called()
    mocker_get_cursor.assert_not_called()
    mocker_get_historic_reports_data.assert_not_called()
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_not_called()
    mocker_close_connection.assert_not_called()


def test_generate_user_historic_reports_should_raise_exception_if_connection_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports
) -> None:

    # Arrange
    mocker_get_connection.side_effect = OperationalError('Connection lost')

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_not_called()
    mocker_get_historic_reports_data.assert_not_called()
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_not_called()
    mocker_close_connection.assert_not_called()


def test_generate_user_historic_reports_should_raise_exception_if_cursor_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value

    mocker_get_cursor.side_effect = OperationalError('Cursor lost')

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_not_called()
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    db_conn.rollback.assert_called_once()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_not_called()
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_raise_exception_if_get_historic_reports_data_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.side_effect = OperationalError(
        'Query failed'
    )

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    db_conn.rollback.assert_called_once()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_raise_exception_if_reports_data_not_found(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.return_value = None

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    db_conn.rollback.assert_not_called()
    mocker_print_exc.assert_not_called()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_raise_exception_if_generate_historic_reports_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month, reports_data, expected_reports_data
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.return_value = reports_data
    mocker_generate_historic_reports.side_effect = IntegrityError(
        'Constraint violation'
    )

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_called_once_with(
        reports_data=expected_reports_data[0],
        db_cursor=db_cursor
    )
    mocker_save_data.assert_not_called()
    db_conn.rollback.assert_called_once()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_raise_exception_if_save_data_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month, reports_data, expected_reports_data
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.return_value = reports_data
    mocker_save_data.side_effect = OperationalError('Connection lost')

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_called_once_with(
        reports_data=expected_reports_data[0],
        db_cursor=db_cursor
    )
    mocker_save_data.assert_called_once_with(
        db_conn=db_conn
    )
    db_conn.rollback.assert_called_once()
    mocker_print_exc.assert_called_once()
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


def test_generate_user_historic_reports_should_exception_if_rollback_fails(
    mocker_get_connection, mocker_get_cursor, mocker_save_data, mocker_datetime,
    mocker_close_connection, mocker_close_cursor, mocker_print_exc,
    mocker_get_historic_reports_data, mocker_generate_historic_reports,
    initial_date_month, final_date_month
) -> None:

    # Arrange
    db_conn = mocker_get_connection.return_value
    db_cursor = mocker_get_cursor.return_value

    mocker_get_historic_reports_data.side_effect = OperationalError(
        'Query failed'
    )
    db_conn.rollback.side_effect = OperationalError('Connection lost')

    # Act
    generate_user_historic_reports()

    # Assert
    mocker_datetime.now.assert_called_once_with(
        tz=timezone.utc
    )
    mocker_get_connection.assert_called_once()
    mocker_get_cursor.assert_called_once_with(
        db_conn=db_conn
    )
    mocker_get_historic_reports_data.assert_called_once_with(
        initial_date_month=initial_date_month,
        final_date_month=final_date_month,
        db_cursor=db_cursor
    )
    mocker_generate_historic_reports.assert_not_called()
    mocker_save_data.assert_not_called()
    db_conn.rollback.assert_called_once()
    assert mocker_print_exc.call_count == 2
    mocker_close_cursor.assert_called_once_with(
        db_cursor=db_cursor
    )
    mocker_close_connection.assert_called_once_with(
        db_conn=db_conn
    )


async def test_get_user_historic_reports_verify_expected_behavior(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection, 
    mocker_close_cursor, mocker_token, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        expected_message = 'Históricos de relatórios buscados com sucesso'

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['success_message']
        assert status_code == 200
        
        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_reports_should_raise_exception_if_request_token_missing(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = (
            'Não foi possível buscar os históricos de relatórios, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_get_historic_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_historic_reports_should_return_error_if_get_connection_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = (
            'Não foi possível buscar os históricos de relatórios, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_get_historic_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_historic_reports_should_return_error_if_get_cursor_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = (
            'Não foi possível buscar os históricos de relatórios, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_reports_should_return_error_if_get_historic_reports_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_historic_reports.side_effect = OperationalError('Query failed')

        expected_message = (
            'Não foi possível buscar os históricos de relatórios, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_reports_should_return_error_if_historic_reports_not_found(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_get_historic_reports, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_historic_reports.return_value = None

        expected_message = (
            'Não foi possível buscar os históricos de relatórios, '
            'históricos não encontrados'
        )

        # Act
        response, status_code = await get_user_historic_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 404

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_report_verify_expected_behavior(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection, 
    mocker_close_cursor, mocker_token, app, mocker_historic_report_id, 
    mocker_get_historic_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        expected_message = 'Histórico de relatório buscado com sucesso'

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['success_message']
        assert status_code == 200
        
        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_report_should_return_error_if_request_token_or_request_historic_report_id_missing(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_get_historic_report, app
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = (
            'Não foi possível buscar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_get_historic_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_historic_report_should_return_error_if_get_connection_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_get_historic_report, app
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = (
            'Não foi possível buscar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_get_historic_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_historic_report_should_return_error_if_get_cursor_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_get_historic_report, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = (
            'Não foi possível buscar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_report_should_return_error_if_get_historic_report_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_get_historic_report, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_historic_report.side_effect = OperationalError('Query failed')

        expected_message = (
            'Não foi possível buscar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_historic_report_should_return_error_if_historic_report_not_found(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_get_historic_report, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_historic_report.return_value = None

        expected_message = (
            'Não foi possível buscar o histórico de relatório, '
            'histórico não encontrado'
        )

        # Act
        response, status_code = await get_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 404

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_delete_user_historic_report_verify_expected_behavior(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection, 
    mocker_close_cursor, mocker_token, app, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert response == ''
        assert status_code == 204
        
        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_delete_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(
            db_conn=db_conn
        )
        db_conn.rollback.assert_not_called()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_delete_user_historic_report_should_raise_exception_if_request_token_or_request_historic_report_id_missing(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_delete_historic_report,
    mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_delete_historic_report.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_delete_user_historic_report_should_raise_exception_if_get_connection_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_delete_historic_report.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_delete_user_historic_report_should_raise_exception_if_get_cursor_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_delete_historic_report.assert_not_called()
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_delete_user_historic_report_should_raise_exception_if_delete_historic_report_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_delete_historic_report.side_effect = OperationalError(
            'Query failed'
        )

        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_delete_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
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


async def test_delete_user_historic_report_should_raise_exception_if_save_data_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_save_data.side_effect = OperationalError('Commit failed')

        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_delete_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
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


async def test_delete_user_historic_report_should_raise_exception_if_rollback_fails(
    mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_token, mocker_historic_report_id,
    mocker_delete_historic_report, mocker_save_data, app
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_delete_historic_report.side_effect = OperationalError(
            'Query failed'
        )
        db_conn.rollback.side_effect = OperationalError('Rollback failed')

        expected_message = (
            'Não foi possível deletar o histórico de relatório, '
            'tente novamente'
        )

        # Act
        response, status_code = await delete_user_historic_report(
            request_token=mocker_token,
            request_historic_report_id=mocker_historic_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_delete_historic_report.assert_called_once_with(
            historic_report_id=mocker_historic_report_id,
            user_id=mocker_token['sub'],
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