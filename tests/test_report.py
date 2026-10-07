from datetime import date, timezone, datetime
from decimal import Decimal

from app.services.report_service import (
    generate_expenses_report, 
    get_user_reports,
    get_user_report
)
from mysql.connector.errors import OperationalError, IntegrityError
import pytest


@pytest.fixture
def mocker_token(mocker):
    token_data = {
        'sub': 1,
        'exp': mocker.ANY
    }

    return token_data

@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'app.services.report_service.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'app.services.report_service.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'app.services.report_service.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'app.services.report_service.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'app.services.report_service.close_cursor'
    )

    return mocked_close_cursor

@pytest.fixture
def mocker_get_calc_expenses(mocker):
    mocked_get_calc_expenses = mocker.patch(
        'app.services.report_service.get_calc_expenses'
    )

    return mocked_get_calc_expenses

@pytest.fixture
def calc_expenses():
    calc_expenses_data = {
        'total_value': Decimal('7950.50'),
        'total_expenses': 3,
        'settled_expenses': 1,
        'overdue_expenses': 0
    }

    return calc_expenses_data

@pytest.fixture
def current_date():
    return date(2026, 10, 6)

@pytest.fixture
def mocker_datetime(mocker, current_date):
    mocked_datetime = mocker.patch(
        'app.services.report_service.datetime'
    )
    mocked_datetime.now.return_value.date.return_value = current_date

    return mocked_datetime

@pytest.fixture
def mocker_generate_report(mocker):
    mocked_generate_report = mocker.patch(
        'app.services.report_service.generate_report'
    )

    return mocked_generate_report

@pytest.fixture
def mocker_get_reports(mocker):
    mocked_get_reports = mocker.patch('app.services.report_service.get_reports')

    return mocked_get_reports

@pytest.fixture
def reports():
    reports_data = [
        {
            'id': 2,
            'user_id': 1,
            'total_value': Decimal('7950.50'),
            'total_expenses': 3,
            'settled_expenses': 1,
            'overdue_expenses': 0,
            'created_at': datetime(2026, 10, 7, 0, 0, 0)
        },
        {
            'id': 1,
            'user_id': 1,
            'total_value': Decimal('2500.00'),
            'total_expenses': 1,
            'settled_expenses': 0,
            'overdue_expenses': 1,
            'created_at': datetime(2026, 10, 6, 0, 0, 0)
        }
    ]

    return reports_data

@pytest.fixture
def report():
    return {
        'id': 1,
        'user_id': 1,
        'total_value': Decimal('2500.00'),
        'total_expenses': 1,
        'settled_expenses': 0,
        'overdue_expenses': 1,
        'created_at': datetime(2026, 10, 6, 0, 0, 0)
    }

@pytest.fixture
def mocker_get_report(mocker):
    mocked_get_report = mocker.patch('app.services.report_service.get_report')

    return mocked_get_report

@pytest.fixture
def mocker_report_id():
    return 1


async def test_generate_expenses_report_verify_expected_behavior(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, calc_expenses, mocker_datetime, current_date,
    mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.return_value = calc_expenses

        expected_message = 'Relatório gerado com sucesso'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['success_message']
        assert status_code == 201

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_called_once_with(tz=timezone.utc)
        mocker_generate_report.assert_called_once_with(
            calc_expenses=calc_expenses,
            current_date=current_date,
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


async def test_generate_expenses_report_should_raise_exception_if_request_token_missing(
    app, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, mocker_datetime, mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_get_calc_expenses.assert_not_called()
        mocker_datetime.now.assert_not_called()
        mocker_generate_report.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_generate_expenses_report_should_return_error_if_get_connection_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, mocker_datetime, mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_not_called()
        mocker_get_calc_expenses.assert_not_called()
        mocker_datetime.now.assert_not_called()
        mocker_generate_report.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_generate_expenses_report_should_return_error_if_get_cursor_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, mocker_datetime, mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_not_called()
        mocker_datetime.now.assert_not_called()
        mocker_generate_report.assert_not_called()
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once_with()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_generate_expenses_report_should_return_error_if_get_calc_expenses_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, mocker_datetime, mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.side_effect = IntegrityError(
            'Constraint violation'
        )

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_not_called()
        mocker_generate_report.assert_not_called()
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once_with()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_generate_expenses_report_should_return_error_if_expenses_not_found(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, mocker_datetime, mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.return_value = None

        expected_message = (
            'Não foi possível gerar o relatório, nenhuma despesa encontrada'
        )

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 404

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_not_called()
        mocker_generate_report.assert_not_called()
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_not_called()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_generate_expenses_report_should_return_error_if_generate_report_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, calc_expenses, mocker_datetime, current_date,
    mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.return_value = calc_expenses
        mocker_generate_report.side_effect = IntegrityError(
            'Constraint violation'
        )

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_called_once_with(tz=timezone.utc)
        mocker_generate_report.assert_called_once_with(
            calc_expenses=calc_expenses,
            current_date=current_date,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once_with()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_generate_expenses_report_should_return_error_if_save_data_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, calc_expenses, mocker_datetime, current_date,
    mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.return_value = calc_expenses
        mocker_save_data.side_effect = OperationalError('Commit failed')

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_called_once_with(tz=timezone.utc)
        mocker_generate_report.assert_called_once_with(
            calc_expenses=calc_expenses,
            current_date=current_date,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(
            db_conn=db_conn
        )
        db_conn.rollback.assert_called_once_with()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_generate_expenses_report_should_return_error_if_rollback_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_save_data, mocker_close_connection, mocker_close_cursor,
    mocker_get_calc_expenses, calc_expenses, mocker_datetime, current_date,
    mocker_generate_report
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_calc_expenses.return_value = calc_expenses
        mocker_generate_report.side_effect = IntegrityError(
            'Constraint violation'
        )
        db_conn.rollback.side_effect = OperationalError('Connection lost')

        expected_message = 'Não foi possível gerar o relatório, tente novamente'

        # Act
        response, status_code = await generate_expenses_report(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once_with()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_calc_expenses.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_datetime.now.assert_called_once_with(tz=timezone.utc)
        mocker_generate_report.assert_called_once_with(
            calc_expenses=calc_expenses,
            current_date=current_date,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_save_data.assert_not_called()
        db_conn.rollback.assert_called_once_with()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_reports_verify_expected_behavior(
    app, mocker_token, mocker_get_connection, mocker_get_cursor, reports,
    mocker_close_connection, mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_reports.return_value = reports

        expected_message = 'Relatórios buscados com sucesso'

        # Act
        response, status_code = await get_user_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['success_message']
        assert reports == response['reports']
        assert isinstance(response['reports'], list)
        assert status_code == 200

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_reports_should_raise_exception_if_request_token_missing(
    app, mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = 'Não foi possível buscar os relatórios, tente novamente'

        # Act
        response, status_code = await get_user_reports(
            request_token=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_get_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_reports_should_return_error_if_get_connection_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = 'Não foi possível buscar os relatórios, tente novamente'

        # Act
        response, status_code = await get_user_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_get_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_reports_should_return_error_if_get_cursor_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = 'Não foi possível buscar os relatórios, tente novamente'

        # Act
        response, status_code = await get_user_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_reports.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_reports_should_return_error_if_get_reports_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_reports.side_effect = OperationalError('Query failed')

        expected_message = 'Não foi possível buscar os relatórios, tente novamente'

        # Act
        response, status_code = await get_user_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_reports_should_return_error_if_reports_not_found(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_reports
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_reports.return_value = None

        expected_message = (
            'Não foi possível buscar os relatórios, nenhum relatório encontrado'
        )

        # Act
        response, status_code = await get_user_reports(
            request_token=mocker_token
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 404

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_reports.assert_called_once_with(
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_report_verify_expected_behavior(
    app, mocker_token, mocker_get_connection, mocker_get_cursor, report,
    mocker_close_connection, mocker_close_cursor, mocker_get_report,
    mocker_report_id
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_report.return_value = report

        expected_message = 'Relatório buscado com sucesso'

        # Act
        response, status_code = await get_user_report(
            request_token=mocker_token,
            request_report_id=mocker_report_id
        )

        # Assert
        assert expected_message == response['success_message']
        assert report == response['report']
        assert status_code == 200

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_report.assert_called_once_with(
            report_id=mocker_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_report_should_raise_exception_if_request_token_or_report_id_missing(
    app, mocker_get_connection, mocker_get_cursor, mocker_close_connection,
    mocker_close_cursor, mocker_get_report
) -> None:

    with app.test_request_context():
        # Arrange
        expected_message = 'Não foi possível buscar o relatório, tente novamente'

        # Act
        response, status_code = await get_user_report(
            request_token=None,
            request_report_id=None
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_get_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_report_should_return_error_if_get_connection_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_report,
    mocker_report_id
) -> None:

    with app.test_request_context():
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_message = 'Não foi possível buscar o relatório, tente novamente'

        # Act
        response, status_code = await get_user_report(
            request_token=mocker_token,
            request_report_id=mocker_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_get_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_get_user_report_should_return_error_if_get_cursor_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_report,
    mocker_report_id
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_message = 'Não foi possível buscar o relatório, tente novamente'

        # Act
        response, status_code = await get_user_report(
            request_token=mocker_token,
            request_report_id=mocker_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_report.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_report_should_return_error_if_get_report_fails(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_report,
    mocker_report_id
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_report.side_effect = OperationalError('Query failed')

        expected_message = 'Não foi possível buscar o relatório, tente novamente'

        # Act
        response, status_code = await get_user_report(
            request_token=mocker_token,
            request_report_id=mocker_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 400

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_report.assert_called_once_with(
            report_id=mocker_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_get_user_report_should_return_error_if_report_not_found(
    app, mocker_token, mocker_get_connection, mocker_get_cursor,
    mocker_close_connection, mocker_close_cursor, mocker_get_report,
    mocker_report_id
) -> None:

    with app.test_request_context():
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value

        mocker_get_report.return_value = None

        expected_message = (
            'Não foi possível buscar o relatório, relatório não encontrado'
        )

        # Act
        response, status_code = await get_user_report(
            request_token=mocker_token,
            request_report_id=mocker_report_id
        )

        # Assert
        assert expected_message == response['error_message']
        assert status_code == 404

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_get_report.assert_called_once_with(
            report_id=mocker_report_id,
            user_id=mocker_token['sub'],
            db_cursor=db_cursor
        )
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )