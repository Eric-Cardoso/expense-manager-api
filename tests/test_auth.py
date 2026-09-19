from mysql.connector.errors import OperationalError, IntegrityError
from app.auth.auth_user import (
    verify_password, 
    generate_access_token, 
    generate_refresh_token
)
from app.auth.decorators import login_required
from app.services.auth_service import login_user, renew_user_session
from app.services.expense_service import manually_enter_expense
import pytest
import os

@pytest.fixture
def user():
    data_user = {
        'email': 'bob@gmail.com',
        'password': 'bob@12345'
    }

    return data_user

@pytest.fixture
def access_token_expiration_time():
    return int(os.getenv('ACCESS_TOKEN_EXPIRATION_TIME', 30))

@pytest.fixture
def refresh_token_expiration_time():
    return int(os.getenv('REFRESH_TOKEN_EXPIRATION_TIME', 7))

@pytest.fixture
def mocker_verify_password(mocker):
    mocked_verify_password = mocker.patch(
        'app.services.auth_service.verify_password'
    )

    return mocked_verify_password

@pytest.fixture
def mocker_generate_access_token(mocker):
    mocked_generate_access_token = mocker.patch(
        'app.services.auth_service.generate_access_token'
    )

    return mocked_generate_access_token

@pytest.fixture
def mocker_generate_refresh_token(mocker):
    mocked_generate_refresh_token = mocker.patch(
        'app.services.auth_service.generate_refresh_token'
    )

    return mocked_generate_refresh_token

@pytest.fixture
def mocker_get_connection(mocker):
    mocked_get_connection = mocker.patch(
        'app.services.auth_service.get_connection'
    )

    return mocked_get_connection

@pytest.fixture
def mocker_get_cursor(mocker):
    mocked_get_cursor = mocker.patch(
        'app.services.auth_service.get_cursor'
    )

    return mocked_get_cursor

@pytest.fixture
def mocker_get_user(mocker):
    mocked_get_user = mocker.patch(
        'app.services.auth_service.get_user_by_email'
    )

    return mocked_get_user

@pytest.fixture
def mocker_insert_token_data(mocker):
    mocked_insert_token_data = mocker.patch(
        'app.services.auth_service.insert_token_data'
    )

    return mocked_insert_token_data

@pytest.fixture
def mocker_update_revoked_token(mocker):
    mocked_update_revoked_token = mocker.patch(
        'app.services.auth_service.update_revoked_token'
    )

    return mocked_update_revoked_token

@pytest.fixture
def mocker_save_data(mocker):
    mocked_save_data = mocker.patch(
        'app.services.auth_service.save_data'
    )

    return mocked_save_data

@pytest.fixture
def mocker_close_connection(mocker):
    mocked_close_connection = mocker.patch(
        'app.services.auth_service.close_connection'
    )

    return mocked_close_connection

@pytest.fixture
def mocker_close_cursor(mocker):
    mocked_close_cursor = mocker.patch(
        'app.services.auth_service.close_cursor'
    )

    return mocked_close_cursor

@pytest.fixture
def mocker_jwt(mocker):
    mocked_jwt = mocker.patch(
        'app.services.auth_service.jwt'
    )

    return mocked_jwt

@pytest.fixture
def mocker_decorator_jwt(mocker):
    mocked_decorator_jwt = mocker.patch('app.auth.decorators.jwt')

    return mocked_decorator_jwt


@pytest.fixture
def mocker_get_user_token_data(mocker):
    mocked_get_user_token_data = mocker.patch(
        'app.services.auth_service.get_user_token_data'
    )

    return mocked_get_user_token_data

@pytest.fixture
def mocker_hash_token(mocker):
    mocked_hash_token = mocker.patch(
        'app.services.auth_service.hashlib'
    )

    return mocked_hash_token

@pytest.fixture
def mocker_request_access_token():
    return {
        'Authorization': (
            'Bearer dGhpcyBpcyBhIHNhbXBsZSByZWZyZXNoIHRva2VuIGV4YW1wbGU'
        )
    }

@login_required
async def fake_insert_expense(request_token):
    return {'success_message': 'Despesa registrada com sucesso'}, 201


async def test_login_user_it_should_return_the_expected_message(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_insert_token_data, mocker_save_data,
    mocker_close_connection, mocker_close_cursor
) -> None:
    
    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        mocker_get_connection.return_value = None
        mocker_get_cursor.return_value = None
        mocker_get_user.return_value = user
        mocker_verify_password.return_value = None
        mocker_generate_access_token.return_value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        mocker_generate_refresh_token.return_value =( 
            'dGhpcyBpcyBhIHNhbXBsZSByZ'
            'WZyZXNoIHRva2VuIGV4YW1wbGU'
        )
        mocker_insert_token_data.return_value = None
        mocker_save_data.return_value = None
        mocker_close_cursor.return_value = None
        mocker_close_connection.return_value = None

        expected_message_success = 'Login realizado com sucesso'
        expected_message_token_type = 'Bearer'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_success == response['success_message']
        assert expected_message_token_type == response['token_type']
        assert response['access_token'] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        assert response['refresh_token'] == (
            'dGhpcyBpcyBhIHNhbXBsZSByZWZyZXNoIHRva2VuIGV4YW1wbGU'
        )
        assert status_code == 200

async def test_login_user_verify_expected_behavior(
    user, mocker, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_insert_token_data, mocker_save_data,
    mocker_close_connection, mocker_close_cursor,
    access_token_expiration_time, refresh_token_expiration_time
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.return_value = user
        mocker_verify_password.return_value = None
        mocker_generate_access_token.return_value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        mocker_generate_refresh_token.return_value =( 
            'dGhpcyBpcyBhIHNhbXBsZSByZ'
            'WZyZXNoIHRva2VuIGV4YW1wbGU'
        )
        mocker_insert_token_data.return_value = None
        mocker_save_data.return_value = None
        mocker_close_cursor.return_value = None
        mocker_close_connection.return_value = None

        expected_message_success = 'Login realizado com sucesso'
        expected_message_token_type = 'Bearer'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_success == response['success_message']
        assert expected_message_token_type == response['token_type']
        assert response['access_token'] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        assert response['refresh_token'] == (
            'dGhpcyBpcyBhIHNhbXBsZSByZWZyZXNoIHRva2VuIGV4YW1wbGU'
        )
        assert status_code == 200

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_get_user.assert_called_once_with(
            user_email=user['email'], db_cursor=db_cursor
        )
        mocker_verify_password.assert_called_once_with(
            password_sent=user['password'], user_password=user['password_hash']
        )
        mocker_generate_access_token.assert_called_once_with(
            user_id=user['id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_called_once_with(
            user_id=user['id'],
            refresh_token_expiration_time=refresh_token_expiration_time
        )
        mocker_insert_token_data.assert_called_once_with(
            token_data={
                'user_id': user['id'],
                'token_hash': mocker.ANY,
                'is_revoked': False,
                'expiration_date': mocker.ANY,
                'created_at': mocker.ANY
            },
            db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(db_conn=db_conn)
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()

async def test_login_user_should_raise_exception_if_connection_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_close_connection, mocker_close_cursor
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        mocker_get_connection.side_effect = OperationalError('Connection lost') 

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_get_user.assert_not_called()
        mocker_verify_password.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_generate_refresh_token.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()

async def test_login_user_should_raise_exception_if_select_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_close_connection, mocker_close_cursor
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.side_effect = IntegrityError('Data invalid') 

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_get_user.assert_called_once_with(
            user_email=user['email'], db_cursor=db_cursor
        )
        mocker_verify_password.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_generate_refresh_token.assert_not_called()
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()


async def test_login_user_should_raise_exception_if_verify_password_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_close_connection, mocker_close_cursor
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.return_value = user
        mocker_verify_password.side_effect = ValueError('Incorrect password')

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_get_user.assert_called_once_with(
            user_email=user['email'], db_cursor=db_cursor
        )
        mocker_verify_password.assert_called_once_with(
            password_sent=user['password'], user_password=user['password_hash']
        )
        mocker_generate_access_token.assert_not_called()
        mocker_generate_refresh_token.assert_not_called()
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()


async def test_login_user_should_raise_exception_if_verify_generate_access_token_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_close_connection, mocker_close_cursor,
    access_token_expiration_time
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.return_value = user
        mocker_verify_password.return_value = None
        mocker_generate_access_token.side_effect = ValueError(
            'Error in access token generation'
        )

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_get_user.assert_called_once_with(
            user_email=user['email'], db_cursor=db_cursor
        )
        mocker_verify_password.assert_called_once_with(
            password_sent=user['password'], user_password=user['password_hash']
        )
        mocker_generate_access_token.assert_called_once_with(
            user_id=user['id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_not_called()
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()


async def test_login_user_should_raise_exception_if_verify_generate_refresh_token_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_close_connection, mocker_close_cursor,
    access_token_expiration_time, refresh_token_expiration_time
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.return_value = user
        mocker_verify_password.return_value = None
        mocker_generate_access_token.return_value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        mocker_generate_refresh_token.side_effect = ValueError(
            'Error in refresh token generation'
        )

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_get_user.assert_called_once_with(
            user_email=user['email'], db_cursor=db_cursor
        )
        mocker_verify_password.assert_called_once_with(
            password_sent=user['password'], user_password=user['password_hash']
        )
        mocker_generate_access_token.assert_called_once_with(
            user_id=user['id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_called_once_with(
            user_id=user['id'],
            refresh_token_expiration_time=refresh_token_expiration_time
        )
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()


async def test_login_user_should_raise_exception_if_insert_token_data_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_get_user, 
    mocker_verify_password, mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_insert_token_data, mocker_save_data,
    mocker_close_connection, mocker_close_cursor,
    access_token_expiration_time, refresh_token_expiration_time
) -> None:

    with app.test_request_context(json=user):
        # Arrange
        user['id'] = 1
        user['password_hash'] = user['password']

        db_conn = mocker_get_connection.return_value
        db_cursor = mocker_get_cursor.return_value
        mocker_get_user.return_value = user
        mocker_verify_password.return_value = None
        mocker_generate_access_token.return_value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        mocker_generate_refresh_token.return_value = (
            'dGhpcyBpcyBhIHNhbXBsZSByZ'
            'WZyZXNoIHRva2VuIGV4YW1wbGU'
        )
        mocker_insert_token_data.side_effect = IntegrityError('Insert failed')

        expected_message_error = 'Não foi possível realizar o login, tente novamente'

        # Act
        response, status_code = await login_user()

        # Assert
        assert expected_message_error == response['error_message']
        assert status_code == 401

        mocker_generate_access_token.assert_called_once_with(
            user_id=user['id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_called_once_with(
            user_id=user['id'],
            refresh_token_expiration_time=refresh_token_expiration_time
        )
        mocker_insert_token_data.assert_called_once()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_called_once()
        mocker_close_connection.assert_called_once()


async def test_verify_password_verify_expected_behavior(mocker, user) -> None:

    # Arrange
    user['password_hash'] = user['password']
    
    mocker_bcrypt = mocker.patch('app.auth.auth_user.bcrypt')

    mocker_checkpw = mocker_bcrypt.checkpw

    mocker_checkpw.return_value = True

    # Act
    verify_password(
        password_sent=user['password'], user_password=user['password_hash']
    )

    # Assert
    mocker_checkpw.assert_called_once_with(
        password=user['password'].encode('utf-8'),
        hashed_password=user['password_hash'].encode('utf-8')
    )


async def test_verify_password_should_raise_exception_if_checkpw_fails(
    mocker, user
) -> None:

    # Arrange
    user['password_hash'] = user['password']
    
    mocker_bcrypt = mocker.patch('app.auth.auth_user.bcrypt')

    mocker_checkpw = mocker_bcrypt.checkpw

    mocker_checkpw.side_effect = ValueError('Incorrect password')

    # Act
    with pytest.raises(ValueError):
        verify_password(
            password_sent=user['password'], user_password=user['password_hash']
        )

    # Assert
    mocker_checkpw.assert_called_once_with(
        password=user['password'].encode('utf-8'),
        hashed_password=user['password_hash'].encode('utf-8')
    )


async def test_generate_access_token_verify_expected_behavior(
    mocker, user, access_token_expiration_time
) -> None:

    # Arrange
    user['id'] = 1

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }

    mocker_jwt = mocker.patch('app.auth.auth_user.jwt')
    mocker_encode = mocker_jwt.encode
    mocker_secret_key = os.getenv('SECRET_KEY')
    mocker_algorithm = os.getenv('ALGORITHM')

    mocker_encode.return_value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'

    expected_response = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'

    # Act
    response = generate_access_token(
        user_id=user['id'], 
        access_token_expiration_time=access_token_expiration_time
    )

    # Assert
    assert expected_response == response

    mocker_encode.assert_called_once_with(
        payload=info_token,
        key=mocker_secret_key,
        algorithm=mocker_algorithm
    )


async def test_generate_access_token_should_raise_exception_if_encode_fails(
    mocker, user, access_token_expiration_time
) -> None:

    # Arrange
    user['id'] = 1

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }

    mocker_jwt = mocker.patch('app.auth.auth_user.jwt')
    mocker_encode = mocker_jwt.encode
    mocker_secret_key = os.getenv('SECRET_KEY')
    mocker_algorithm = os.getenv('ALGORITHM')

    mocker_encode.side_effect  = ValueError('Invalid arguments')

    # Act
    with pytest.raises(ValueError):
        generate_access_token(
            user_id=user['id'], 
            access_token_expiration_time=access_token_expiration_time
        )

    # Assert
    mocker_encode.assert_called_once_with(
        payload=info_token,
        key=mocker_secret_key,
        algorithm=mocker_algorithm
    )


async def test_generate_refresh_token_verify_expected_behavior(
    mocker, user, refresh_token_expiration_time
) -> None:

    # Arrange
    user['id'] = 1

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }

    mocker_jwt = mocker.patch('app.auth.auth_user.jwt')
    mocker_encode = mocker_jwt.encode
    mocker_secret_key = os.getenv('SECRET_KEY')
    mocker_algorithm = os.getenv('ALGORITHM')

    mocker_encode.return_value = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
    )

    expected_response = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
    )

    # Act
    response = generate_refresh_token(
        user_id=user['id'], 
        refresh_token_expiration_time=refresh_token_expiration_time
    )

    # Assert
    assert expected_response == response

    mocker_encode.assert_called_once_with(
        payload=info_token,
        key=mocker_secret_key,
        algorithm=mocker_algorithm
    )


async def test_generate_refresh_token_should_raise_exception_if_encode_fails(
    mocker, user, refresh_token_expiration_time
) -> None:

    # Arrange
    user['id'] = 1

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }

    mocker_jwt = mocker.patch('app.auth.auth_user.jwt')
    mocker_encode = mocker_jwt.encode
    mocker_secret_key = os.getenv('SECRET_KEY')
    mocker_algorithm = os.getenv('ALGORITHM')

    mocker_encode.side_effect  = ValueError('Invalid arguments')

    # Act
    with pytest.raises(ValueError):
        generate_refresh_token(
            user_id=user['id'],
            refresh_token_expiration_time=refresh_token_expiration_time
        )

    # Assert
    mocker_encode.assert_called_once_with(
        payload=info_token,
        key=mocker_secret_key,
        algorithm=mocker_algorithm
    )


async def test_renew_user_session_verify_expected_behavior(
    user, app, mocker, mocker_hash_token, mocker_get_connection, 
    mocker_get_cursor, mocker_jwt, mocker_get_user_token_data, 
    mocker_close_connection, mocker_close_cursor, mocker_generate_access_token, 
    mocker_generate_refresh_token, mocker_insert_token_data,
    mocker_update_revoked_token, mocker_save_data,
    access_token_expiration_time, refresh_token_expiration_time
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }
    
    with app.test_request_context(json=refresh_token):

        info_token = {
            'sub': str(user['id']),
            'exp': mocker.ANY
        }

        user_token_data = {
            'user_id': 1,
            'token_hash': 'IUzI1NiIsInR5cC5cCI6II1NiIsIn',
            'is_revoked': False,
            'expiration_date': mocker.ANY,
            'created_at': mocker.ANY    
        }

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token

        db_conn = mocker_get_connection.return_value

        db_cursor = mocker_get_cursor.return_value 

        mocker_sha256 = mocker_hash_token.sha256

        mocker_sha256.return_value.hexdigest.return_value = (
            'IUzI1NiIsInR5cC5cCI6II1NiIsIn'
        )

        mocker_get_user_token_data.return_value = user_token_data

        mocker_generate_access_token.return_value = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        )

        mocker_generate_refresh_token.return_value = (
            'bmV3X3JlZnJlc2hfdG9rZW5fZXhhbXBsZQ'
        )

        mocker_insert_token_data.return_value = None
        mocker_update_revoked_token.return_value = None
        mocker_save_data.return_value = None

        expected_message_success = 'Sessão renovada com sucesso'

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_message_success == response['success_message']
        assert response['access_token'] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        assert response['refresh_token'] == 'bmV3X3JlZnJlc2hfdG9rZW5fZXhhbXBsZQ'
        assert status_code == 200

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(db_conn=db_conn)
        mocker_sha256.assert_any_call(
            refresh_token['refresh_token'].encode('utf-8')
        )
        mocker_sha256.assert_any_call(
            'bmV3X3JlZnJlc2hfdG9rZW5fZXhhbXBsZQ'.encode('utf-8')
        )
        mocker_get_user_token_data.assert_called_once_with(
            hashed_token=mocker_sha256.return_value.hexdigest.return_value, 
            db_cursor=db_cursor
        )
        mocker_generate_access_token.assert_called_once_with(
            user_id=user_token_data['user_id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_called_once_with(
            user_id=user_token_data['user_id'],
            refresh_token_expiration_time=refresh_token_expiration_time
        )
        mocker_insert_token_data.assert_called_once_with(
            token_data={
                'user_id': user_token_data['user_id'],
                'token_hash': mocker.ANY,
                'is_revoked': False,
                'expiration_date': mocker.ANY,
                'created_at': mocker.ANY
            },
            db_cursor=db_cursor
        )
        mocker_update_revoked_token.assert_called_once_with(
            hashed_token=user_token_data['token_hash'], db_cursor=db_cursor
        )
        mocker_save_data.assert_called_once_with(db_conn=db_conn)
        mocker_close_cursor.assert_called_once_with(db_cursor=db_cursor)
        mocker_close_connection.assert_called_once_with(db_conn=db_conn)


async def test_renew_user_should_raise_exception_if_decode_fails(
    user, app, mocker_get_connection, mocker_get_cursor, mocker_jwt, 
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_hash_token  
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.side_effect = ValueError('Invalid Token')

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_not_called()
        mocker_get_cursor.assert_not_called()
        mocker_hash_token.sha256.assert_not_called()
        mocker_get_user_token_data.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_renew_user_should_raise_exception_if_connection_fails(
    user, app, mocker, mocker_get_connection, mocker_get_cursor, mocker_jwt, 
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_hash_token   
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token 

        mocker_get_connection.side_effect = OperationalError('Connection lost')

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_not_called()
        mocker_hash_token.sha256.assert_not_called()
        mocker_get_user_token_data.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_not_called()


async def test_renew_user_should_raise_exception_if_cursor_fails(
    user, app, mocker, mocker_get_connection, mocker_get_cursor, mocker_jwt, 
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_hash_token 
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token 

        db_conn = mocker_get_connection.return_value

        mocker_get_cursor.side_effect = OperationalError('Cursor lost')

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_hash_token.sha256.assert_not_called()
        mocker_get_user_token_data.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_close_cursor.assert_not_called()
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_renew_user_should_raise_exception_if_hash_token_fails(
    user, app, mocker, mocker_get_connection, mocker_get_cursor, mocker_jwt, 
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_hash_token
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token 

        db_conn = mocker_get_connection.return_value

        db_cursor = mocker_get_cursor.return_value

        mocker_sha256 = mocker_hash_token.sha256
    
        mocker_sha256.return_value.hexdigest.side_effect = ValueError(
            'Token hash failed'
        )

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_sha256.assert_called_once_with(
            refresh_token['refresh_token'].encode('utf-8')
        )
        mocker_get_user_token_data.assert_not_called()
        mocker_generate_access_token.assert_not_called()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_renew_user_should_raise_exception_if_get_user_token_data_fails(
    user, app, mocker, mocker_get_connection, mocker_get_cursor, mocker_jwt, 
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_hash_token
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token 

        db_conn = mocker_get_connection.return_value

        db_cursor = mocker_get_cursor.return_value

        mocker_sha256 = mocker_hash_token.sha256
    
        mocker_sha256.return_value.hexdigest.return_value = (
            'IUzI1NiIsInR5cC5cCI6II1NiIsIn'
        )

        mocker_get_user_token_data.side_effect = IntegrityError(
            'Token not found'
        )

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_sha256.assert_called_once_with(
            refresh_token['refresh_token'].encode('utf-8')
        )
        mocker_get_user_token_data.assert_called_once_with(
            hashed_token=mocker_sha256.return_value.hexdigest.return_value, 
            db_cursor=db_cursor
        )
        mocker_generate_access_token.assert_not_called()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn
        )


async def test_renew_user_should_raise_exception_if_generate_access_token_fails(
    user, mocker_hash_token, mocker, mocker_get_connection, mocker_get_cursor,  
    mocker_get_user_token_data, mocker_close_connection, mocker_close_cursor, 
    mocker_generate_access_token, mocker_generate_refresh_token,
    mocker_insert_token_data, mocker_update_revoked_token, mocker_save_data,
    app, access_token_expiration_time, mocker_jwt
) -> None:

    # Arrange
    user['id'] = 1
    refresh_token = {
        'refresh_token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    info_token = {
        'sub': str(user['id']),
        'exp': mocker.ANY
    }

    user_token_data = {
        'user_id': 1,
        'token_hash': 'IUzI1NiIsInR5cC5cCI6II1NiIsIn',
        'is_revoked': False,
        'expiration_date': mocker.ANY,
        'created_at': mocker.ANY    
    }
    
    with app.test_request_context(json=refresh_token):

        mocker_decode = mocker_jwt.decode

        mocker_decode.return_value = info_token 

        db_conn = mocker_get_connection.return_value

        db_cursor = mocker_get_cursor.return_value

        mocker_sha256 = mocker_hash_token.sha256
    
        mocker_sha256.return_value.hexdigest.return_value = (
            'IUzI1NiIsInR5cC5cCI6II1NiIsIn'
        )

        mocker_get_user_token_data.return_value = user_token_data

        mocker_generate_access_token.side_effect = ValueError('Invalid data')

        expected_error_message = (
            'Não foi possível renovar sua sessão, tente novamente'
        )

        # Act
        response, status_code = await renew_user_session()

        # Assert
        assert expected_error_message == response['error_message']
        assert status_code == 401

        mocker_decode.assert_called_once_with(
            jwt=refresh_token['refresh_token'],
            key=os.getenv('SECRET_KEY'),
            algorithms=[os.getenv('ALGORITHM')]
        )

        mocker_get_connection.assert_called_once()
        mocker_get_cursor.assert_called_once_with(
            db_conn=db_conn
        )
        mocker_sha256.assert_called_once_with(
            refresh_token['refresh_token'].encode('utf-8')
        )
        mocker_get_user_token_data.assert_called_once_with(
            hashed_token=mocker_sha256.return_value.hexdigest.return_value, 
            db_cursor=db_cursor
        )
        mocker_generate_access_token.assert_called_once_with(
            user_id=user_token_data['user_id'],
            access_token_expiration_time=access_token_expiration_time
        )
        mocker_generate_refresh_token.assert_not_called()
        mocker_insert_token_data.assert_not_called()
        mocker_update_revoked_token.assert_not_called()
        mocker_save_data.assert_not_called()
        mocker_close_cursor.assert_called_once_with(
            db_cursor=db_cursor
        )
        mocker_close_connection.assert_called_once_with(
            db_conn=db_conn,
        )


async def test_auth_logic_verify_expected_behavior(
    app, mocker, mocker_decorator_jwt, mocker_request_access_token
) -> None:

    info_token = {
        'sub': str(1),
        'exp': mocker.ANY
    }

    with app.test_request_context(
        headers=mocker_request_access_token
    ):
        # Arrange
        mocker_decode = mocker_decorator_jwt.decode

        mocker_decode.return_value = info_token

        expected_message = 'Despesa registrada com sucesso'

        # Act
        response, status_code = await fake_insert_expense()

        # Assert
        assert expected_message == response['success_message']
        assert status_code == 201
        
        mocker_decode.assert_called_once_with(
            jwt=mocker_request_access_token['Authorization'].split()[1], 
            key=os.getenv('SECRET_KEY'), 
            algorithms=[os.getenv('ALGORITHM')]
        )


async def test_auth_logic_should_raise_exception_if_request_token_missing(
    app, mocker_decorator_jwt
) -> None:


    with app.test_request_context():
        # Arrange
        expected_message = 'Operação inválida'

        # Act
        response, status_code = await fake_insert_expense()

        # Assert
        assert expected_message == response['message_error']
        assert status_code == 401
        
        mocker_decorator_jwt.decode.assert_not_called()


async def test_auth_logic_should_raise_exception_if_bearer_prefix_missing(
    app, mocker_decorator_jwt
) -> None:

    fake_request_access_token = {
        'Authorization':(
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.iIsInR5cCI6IkJhbGciugfD4'
        )
    }

    with app.test_request_context(
        headers=fake_request_access_token
    ):
        # Arrange
        expected_message = 'Operação inválida'

        # Act
        response, status_code = await fake_insert_expense()

        # Assert
        assert expected_message == response['message_error']
        assert status_code == 401
        
        mocker_decorator_jwt.decode.assert_not_called()


async def test_auth_logic_should_raise_execption_if_decode_fails(
    app, mocker_decorator_jwt, mocker_request_access_token
) -> None:

    with app.test_request_context(
        headers=mocker_request_access_token
    ):
        # Arrange
        mocker_decode = mocker_decorator_jwt.decode

        mocker_decode.side_effect = ValueError('Token invalid')

        expected_message = 'Operação inválida'

        # Act
        response, status_code = await fake_insert_expense()

        # Assert
        assert expected_message == response['message_error']
        assert status_code == 401
        
        mocker_decode.assert_called_once_with(
            jwt=mocker_request_access_token['Authorization'].split()[1], 
            key=os.getenv('SECRET_KEY'), 
            algorithms=[os.getenv('ALGORITHM')]
        )