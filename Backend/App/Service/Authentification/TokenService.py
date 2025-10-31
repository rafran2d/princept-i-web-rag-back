from App.Models.RefreshTokenModel import RefreshTokenModel
from App.database import AsyncSessionLocal
from App.Schema.UserShcema import UserOutput
from App.Schema.RefreshTokenSchema import RefreshTokenInput, RefreshTokenOutput
from dotenv import load_dotenv
from datetime import datetime, timedelta,timezone
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from jwt import InvalidTokenError,ExpiredSignatureError
from App.Exception.TokenException import (
    CreateTokenError,
    ReadTokenError,
    RevokeTokenError
)
import os
import jwt
import secrets
import uuid
import hmac
import base64
import hashlib

load_dotenv()

SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")


def generate_access_token(user_output: UserOutput) -> str:
    """
    Generate a signed JWT access token for a given user.

    This function creates a JWT containing user information such as ID, email, role, and status.
    The token also includes an expiration time and issued-at timestamp.

    Args:
        user_output (UserOutput): The user data used to create the token payload.

    Returns:
        str: The encoded JWT access token.

    Raises:
        Exception: If token generation fails for any reason.
    """
    try:
        payload = {
            "sub": str(user_output.id),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRES))).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "email": user_output.email,
            "role": user_output.role,
            "status": user_output.status
        }
        access_token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

        return access_token
    
    except InvalidTokenError as e:
        raise Exception(f"Failed to generate access_token. Original Error {e}")
    
    except Exception as e:
        raise Exception(f"Failed to generate access_token. Original Error : {e}")
    

def verify_access_token(access_token: str):
    """
    Verifies the authenticity of a JWT access token.

    This function decodes the given JWT using the SECRET_KEY and checks its validity.
    It raises an exception if the token is expired or invalid.

    Args:
        access_token (str): The JWT access token to verify.

    Returns:
        dict: The decoded payload of the token if valid.

    Raises:
        ExpiredSignatureError: If the token has expired.
        InvalidTokenError: If the token is invalid or tampered.
    """
    try:
        payload = jwt.decode(access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except ExpiredSignatureError:
        raise ExpiredSignatureError("The token has expired")
    
    except InvalidTokenError:
        raise InvalidTokenError("Invalid token or tampered")

def generate_refresh_token():
    """
    Generate a secure random refresh token.

    This function uses Python's `secrets` module to create a 64-byte URL-safe token.

    Returns:
        str: A randomly generated refresh token.
    """
    token = secrets.token_urlsafe(64)
    return token


def hash_token(token: str) -> str:
    """
    Hashes a refresh token before storing it in the database.

    This function uses the HMAC algorithm (based on SHA-256) combined with a secret key
    to generate a unique, non-reversible hash of the token.
    The resulting hash is Base64-encoded to make it readable and easy to store in the database.

    Args:
        token (str): The plain-text refresh token to hash.

    Returns:
        str: The Base64-encoded hash of the token, ready to be stored in the database.
    """
    mac = hmac.new(SECRET_KEY.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode()


async def create_refresh_token(token: RefreshTokenInput) -> RefreshTokenOutput:
    """
    Create and store a hashed refresh token in the database.

    Args:
        token (RefreshTokenInput): The refresh token input containing user_id and token.

    Returns:
        RefreshTokenOutput: The stored refresh token record.

    Raises:
        CreateTokenError: If an error occurs while creating or saving the token.
    """
    try:
        hashed_token = hash_token(token.token)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                refreshtoken = RefreshTokenModel(
                    user_id=token.user_id,
                    hashed_token=hashed_token
                )
                session.add(refreshtoken)
                await session.flush()

                return RefreshTokenOutput.from_orm(refreshtoken)
    except (SQLAlchemyError, Exception) as e:
        raise CreateTokenError(f"Failed to create the token. Original Error {e}")




async def read_refresh_token(hashed_token : str)->RefreshTokenOutput:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(RefreshTokenModel).where(RefreshTokenModel.hashed_token == hashed_token)
                response = await session.execute(stmt)
                token_obj = response.scalars().first() 

        return RefreshTokenOutput.from_orm(token_obj)       

    except (SQLAlchemyError, Exception) as e:
        raise ReadTokenError(f"Failed to read the token. Original Error: {e}")


async def set_revoked_token(token_id: uuid.UUID):
    """
    Mark a refresh token as revoked in the database.

    Args:
        token_id (uuid.UUID): The unique identifier of the refresh token to revoke.

    Raises:
        RevokeTokenError: If an error occurs while revoking the token.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == token_id)
                response = await session.execute(stmt)
                token_obj = response.scalars().first()
                token_obj.revoked = True

    except (SQLAlchemyError, Exception) as e:
        raise RevokeTokenError(f"Failed to revoke the token with the id {token_id}")
