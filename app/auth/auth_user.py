from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy
import bcrypt

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


