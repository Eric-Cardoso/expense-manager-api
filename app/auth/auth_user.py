from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy
import bcrypt
import jwt
import os


load_dotenv()


def validate_user_email(user_email: str) -> None:
    try:
        validate_email(user_email)
    except EmailNotValidError as error:
        raise error

def validate_user_password(user_password: str) -> None: 
    policy = PasswordPolicy.from_names(
        length=8, uppercase=1, numbers=1, special=1
    )

    errors = policy.test(password=user_password)

    if errors:
        raise ValueError(f'Senha não atende aos critérios: {errors}')

def encrypt_password(user_password: str) -> bytes:
    hashed_password = bcrypt.hashpw(
        password=user_password.encode('utf-8'), salt=bcrypt.gensalt()
    )

    return hashed_password

def verify_password(password_sent: str, user_password: str) -> None:
    password_valid = bcrypt.checkpw(
        password=password_sent.encode('utf-8'), 
        hashed_password=user_password.encode('utf-8')
    )

    if not password_valid:
        raise ValueError('Incorrect password')


def generate_access_token(
        user_id: int, access_token_expiration_time: int = 30
    ) -> str:

    try:
        info_token = {
            'sub': str(user_id),
            'exp': datetime.now(timezone.utc) + timedelta(
                minutes=access_token_expiration_time
            )
        }

        access_token = jwt.encode(
            payload=info_token, 
            key=os.getenv('SECRET_KEY'), 
            algorithm=os.getenv('ALGORITHM')
        )

        return access_token
    except Exception:
        raise

def generate_refresh_token(
        user_id: int,  refresh_token_expiration_time: int = 7
    ) -> str:

    info_token = {
        'sub': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(
            days=refresh_token_expiration_time
        )
    }
    
    refresh_token = jwt.encode(
        payload=info_token, 
        key=os.getenv('SECRET_KEY'), 
        algorithm=os.getenv('ALGORITHM')
    )

    return refresh_token




