from app.services.user_service import (
    register_user, 
    validate_user_email, 
    validate_user_password
)
from email_validator import EmailNotValidError
from mysql.connector.errors import OperationalError, IntegrityError
import pytest

@pytest.fixture
def user():
    data_user = {
        'name': 'Bob',
        'email': 'bob@gmail.com',
        'password': 'bob@12345'
    }

    return data_user

@pytest.fixture
def mocker_email(mocker):
    mocked_email = mocker.patch('app.services.user_service.validate_user_email')

    return mocked_email

@pytest.fixture
def mocker_password(mocker):
    mocked_password = mocker.patch(
        'app.services.user_service.validate_user_password'
    )

    return mocked_password

@pytest.fixture
def mocker_password_hash(mocker):
    mocked_password = mocker.patch(
        'app.services.user_service.encrypt_password'
    )

    return mocked_password

@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'app.services.user_service.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'app.services.user_service.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_insert_user(mocker):
    mocked_insert_user = mocker.patch(
        'app.services.user_service.insert_user'
    )

    return mocked_insert_user

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'app.services.user_service.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'app.services.user_service.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'app.services.user_service.close_cursor'
    )

    return mocked_close_cursor


async def test_register_user_should_return_successfully_registered_user(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection, 
    mocker_get_cursor, mocker_insert_user, mocker_save_data, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = None

        mocker_get_connection.return_value = None

        mocker_get_cursor.return_value = None

        mocker_insert_user.return_value = None

        mocker_save_data.return_value = None

        expected_response = 'Usuário cadastrado com sucesso'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_success']
        assert status_code == 200


async def test_register_user_should_call_dependencies_with_correct_arguments(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection,
    mocker_get_cursor, mocker_insert_user, mocker_save_data,
    mocker_close_connection, mocker_close_cursor, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = 'weorkm543256yhbvfd234w2w'

        mocked_conn = mocker_get_connection.return_value

        mocked_cursor = mocker_get_cursor.return_value

        mocker_insert_user.return_value = None

        mocker_save_data.return_value = None

        expected_response = 'Usuário cadastrado com sucesso'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_success']
        assert status_code == 200

        mocker_email.assert_called_once_with(
            user_email=user['email']
        )
        mocker_password.assert_called_once_with(
            user_password=user['password']
        )
        mocker_password_hash.assert_called_once_with(
            user_password=user['password']
        )
        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=mocked_conn)
        mocker_insert_user.assert_called_once_with(
            data_user={
                'name': user['name'],
                'email': user['email'],
                'password': 'weorkm543256yhbvfd234w2w'
            },
            db_cursor=mocked_cursor
        )
        mocker_save_data.assert_called_once_with(db_conn=mocked_conn)
        mocker_close_cursor.assert_called_once_with(db_cursor=mocked_cursor)
        mocker_close_connection.assert_called_once_with(db_conn=mocked_conn)
        mocked_conn.rollback.assert_not_called()


async def test_register_user_should_raise_exception_if_connection_fails(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection,
    mocker_get_cursor, mocker_insert_user, mocker_save_data,
    mocker_close_connection, mocker_close_cursor, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = 'weorkm543256yhbvfd234w2w'

        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_response = 'Erro ao finalizar cadastro, tente novamente'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_error']
        assert status_code == 400

        mocker_email.assert_called_once_with(
            user_email=user['email']
        )
        mocker_password.assert_called_once_with(
            user_password=user['password']
        )
        mocker_password_hash.assert_called_once_with(
            user_password=user['password']
        )
        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_insert_user.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_register_user_should_raise_exception_if_execute_fails(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection,
    mocker_get_cursor, mocker_insert_user, mocker_save_data,
    mocker_close_connection, mocker_close_cursor, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = 'weorkm543256yhbvfd234w2w'

        mocked_conn = mocker_get_connection.return_value

        mocked_cursor = mocker_get_cursor.return_value

        mocker_insert_user.side_effect = IntegrityError(
            'Constraint violation'
        )

        expected_response = 'Erro ao finalizar cadastro, tente novamente'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_error']
        assert status_code == 400

        mocker_email.assert_called_once_with(
            user_email=user['email']
        )
        mocker_password.assert_called_once_with(
            user_password=user['password']
        )
        mocker_password_hash.assert_called_once_with(
            user_password=user['password']
        )
        mocker_get_connection.assert_called_once()
        mocker_insert_user.assert_called_once()
        mocker_save_data.assert_not_called()
        mocked_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_called_once_with(db_cursor=mocked_cursor)
        mocker_close_connection.assert_called_once_with(db_conn=mocked_conn)

async def test_register_user_should_raise_exception_if_commit_fails(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection,
    mocker_get_cursor, mocker_insert_user, mocker_save_data,
    mocker_close_connection, mocker_close_cursor, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = 'weorkm543256yhbvfd234w2w'

        mocked_conn = mocker_get_connection.return_value

        mocked_cursor = mocker_get_cursor.return_value

        mocker_insert_user.return_value = None

        mocker_save_data.side_effect = OperationalError('Connection lost')

        expected_response = 'Erro ao finalizar cadastro, tente novamente'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_error']
        assert status_code == 400

        mocker_email.assert_called_once_with(
            user_email=user['email']
        )
        mocker_password.assert_called_once_with(
            user_password=user['password']
        )
        mocker_password_hash.assert_called_once_with(
            user_password=user['password']
        )
        mocker_get_connection.assert_called_once()
        mocker_insert_user.assert_called_once()
        mocker_save_data.assert_called_once()
        mocked_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_called_once_with(db_cursor=mocked_cursor)
        mocker_close_connection.assert_called_once_with(db_conn=mocked_conn)

async def test_register_user_should_raise_exception_if_rollback_fails(
    mocker_email, mocker_password, mocker_password_hash, mocker_get_connection,
    mocker_get_cursor, mocker_insert_user, mocker_save_data,
    mocker_close_connection, mocker_close_cursor, user, app
) -> None:

    with app.test_request_context(json=user):

        # Arrange
        mocker_email.return_value = None

        mocker_password.return_value = None

        mocker_password_hash.return_value = 'weorkm543256yhbvfd234w2w'

        mocked_conn = mocker_get_connection.return_value

        mocked_cursor = mocker_get_cursor.return_value

        mocker_insert_user.side_effect = IntegrityError('Constraint violation')

        mocked_conn.rollback.side_effect = OperationalError('Connection lost')

        expected_response = 'Erro ao finalizar cadastro, tente novamente'

        # Act
        response, status_code = await register_user()

        # Assert
        assert expected_response == response['message_error']
        assert status_code == 400

        mocker_email.assert_called_once_with(
            user_email=user['email']
        )
        mocker_password.assert_called_once_with(
            user_password=user['password']
        )
        mocker_password_hash.assert_called_once_with(
            user_password=user['password']
        )
        mocker_get_connection.assert_called_once()
        mocker_insert_user.assert_called_once()
        mocker_save_data.assert_not_called()
        mocked_conn.rollback.assert_called_once()
        mocker_close_cursor.assert_called_once_with(db_cursor=mocked_cursor)
        mocker_close_connection.assert_called_once_with(db_conn=mocked_conn)

async def test_validate_user_email_verify_expected_behavior(
    user, mocker
) -> None:
    # Arrange
    mocker_validator = mocker.patch('app.auth.auth_user.validate_email')

    mocker_validator.return_value = None

    # Act
    validate_user_email(user_email=user['email'])

    # Assert
    mocker_validator.assert_called_once()

async def test_validate_user_email_should_raise_exception_if_email_invalid(
    user, mocker
) -> None:
    # Arrange
    mocker_validator = mocker.patch('app.auth.auth_user.validate_email')

    mocker_validator.side_effect = EmailNotValidError('Email invalid')

    # Act
    with pytest.raises(EmailNotValidError):
        validate_user_email(user_email=user['email'])

    # Assert
    mocker_validator.assert_called_once()

async def test_validate_user_password_verify_expected_behavior(
    user, mocker
) -> None:
    # Arrange
    mocker_validator = mocker.patch(
        'app.auth.auth_user.PasswordPolicy'
    )

    mocker_policy = mocker_validator.from_names.return_value

    mocker_test_password = mocker_policy.test

    mocker_test_password.return_value = None

    # Act
    validate_user_password(user_password=user['password'])

    # Assert
    mocker_validator.from_names.assert_called_once()
    mocker_test_password.assert_called_once()

async def test_validate_user_password_should_raise_exception_if_password_invalid(
    user, mocker
) -> None:
    # Arrange
    mocker_validator = mocker.patch(
        'app.auth.auth_user.PasswordPolicy'
    )

    mocker_policy = mocker_validator.from_names.return_value
    
    mocker_test_errors = mocker_policy.test

    mocker_test_errors.side_effect = ValueError('Invalid password')

    # Act
    with pytest.raises(ValueError):
        validate_user_password(user_password=user['password'])

    # Assert
    mocker_validator.from_names.assert_called_once()
    mocker_test_errors.assert_called_once()