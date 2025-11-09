from App.Exception.UserException import (
    UserCreateError,
    EmailAlreadyUsedError,
    ReadUserError,
    UserNotFoundError,
    UserNotFoundError,
    DeleteUserError,
    IncorrectPasswordError,
    EmailStructError
)
from App.Models.UserModel import UserModel as Model,statususer
from App.Schema.UserShcema import UserInput, UserOutput,UserInternalOutput, statususer,UserExternalInput,UserExternalInputSG,RoleEnum
from App.database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr, ValidationError
import bcrypt
import uuid


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    This function returns a UTF-8 string suitable for storage in a database.
    The hash can later be verified with `verify_password`.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password as a UTF-8 string.
    """
    # Generate the bcrypt hash as bytes
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Convert to UTF-8 string for storage
    return hashed_bytes.decode('utf-8')


async def compare_passwd(user : UserExternalInput)  :
    """
    Compare a plain-text password with the hashed password of a user retrieved from the database.

    Args:
        user (UserInput): Pydantic model containing email and password.

    Returns:
        bool: True if the password matches, otherwise raise an error.
        UserInternalOutput: Representation of the user

    Raises:
        IncorrectPasswordError: For an incorrect password.
        Exception: For any other unexpected errors.
    """
    try :
        user_obj = await read_user_email(user.email)

        if bcrypt.checkpw(user.password.encode("utf-8"), user_obj.hashed_password.encode("utf-8")) :
            return True , user_obj
        
        else :
            raise IncorrectPasswordError(f"The password : {user.password} is incorrect")


    except Exception as e :
        raise 


async def create_user(user_input: UserExternalInputSG) -> UserOutput :
    """
    Create a new user in the database with a hashed password.

    Args:
        user_input (UserInput): Pydantic model containing user data (email, display_name, password, role).

    Returns:
        UserOutput: Pydantic model representing the newly created user.

    Raises:
        UserCreateError: If the user cannot be created due to a database error.
        EmailAlreadyUsedError: If the email is already used by another user.
        EmailStruct: If the email format is invalid.
    """
    try :
        if await if_email_exist(user_input.email) :
            raise EmailAlreadyUsedError(f"The email : {user_input.email} is already used")
        
        else :
            hashed_password = hash_password(user_input.password)

            async with AsyncSessionLocal() as session :  #start communication with the db 
                async with session.begin() : #start the conversation
                    new_user = Model(
                        email=user_input.email,
                        display_name=user_input.display_name,
                        hashed_password=hashed_password
                    )
                    session.add(new_user)
                    await session.flush() #send the modification without commiting yet

            return UserOutput.from_orm(new_user)

    except ValidationError as e :
        raise EmailStructError(f"The email {user_input.email} is not valid. Original Error :{e}") from e

    except EmailAlreadyUsedError :
        raise

    except (SQLAlchemyError, Exception) as e :
        raise UserCreateError(f"Failed to create the user {user_input.display_name}.Original error:{e}") from e



async def create_user_admin(user_input: UserExternalInputSG) -> UserOutput :
    """
    Create a new user in the database with a hashed password.

    Args:
        user_input (UserInput): Pydantic model containing user data (email, display_name, password, role).

    Returns:
        UserOutput: Pydantic model representing the newly created user.

    Raises:
        UserCreateError: If the user cannot be created due to a database error.
        EmailAlreadyUsedError: If the email is already used by another user.
        EmailStruct: If the email format is invalid.
    """
    try :
        if await if_email_exist(user_input.email) :
            raise EmailAlreadyUsedError(f"The email : {user_input.email} is already used")
        
        else :
            hashed_password = hash_password(user_input.password)

            async with AsyncSessionLocal() as session :  #start communication with the db 
                async with session.begin() : #start the conversation
                    new_user = Model(
                        email=user_input.email,
                        display_name=user_input.display_name,
                        hashed_password=hashed_password,
                        status=statususer.approved,
                        role=RoleEnum.admin
                    )
                    session.add(new_user)
                    await session.flush() #send the modification without commiting yet

            return UserOutput.from_orm(new_user)

    except ValidationError as e :
        raise EmailStructError(f"The email {user_input.email} is not valid. Original Error :{e}") from e

    except EmailAlreadyUsedError :
        raise

    except (SQLAlchemyError, Exception) as e :
        raise UserCreateError(f"Failed to create the user {user_input.display_name}.Original error:{e}") from e



async def read_user_email(email : EmailStr) -> UserInternalOutput :
    """
    Retrieve a user from the database by their email.

    Args:
        email (EmailStr): The email of the user to retrieve.

    Returns:
        UserOutput : Pydantic model of the user if found.

    Raises:
        EmailNotFoundError: If the email is not linked to any user in the database
        ReadUserError: If there is an error reading the user from the database.
    """
    try :
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(Model).where(Model.email == email)
                response = await session.execute(stmt)
                user_obj = response.scalars().first()

                if user_obj :
                    return UserInternalOutput.from_orm(user_obj)
                
                else : 
                    raise UserNotFoundError(f"User with email: {email} not found")

    except UserNotFoundError :
        raise

    except (SQLAlchemyError,Exception) as e :
        raise ReadUserError(f"Failed to read the user with the email : {e} ")


async def read_registers() -> list[UserOutput] | None:
    """
    Retrieve all users from the database who have a 'pending' status.

    Returns:
        list[UserOutput] | None: 
            A list of Pydantic models representing users with a pending status, 
            or None if no users are found.

    Raises:
        SQLAlchemyError: If there is an error while reading the users from the database.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(Model).where(Model.status == statususer.pending)
                response = await session.execute(stmt)
                user_obj = response.scalars().all()
                
                if user_obj:
                    return [UserOutput.from_orm(user) for user in user_obj]
                else:
                    return None
    
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Failed to read registers. Original error: {e}")


async def read_user_id(user_id: uuid.UUID) -> UserOutput:
    """
    Retrieve a user from the database by their unique ID.

    This function fetches a user record using its UUID and returns a serialized
    `UserOutput` schema if found. If the user does not exist, a `UserNotFoundError`
    is raised.

    Args:
        user_id (uuid.UUID): The unique identifier of the user to retrieve.

    Returns:
        UserOutput: The user data retrieved from the database.

    Raises:
        UserNotFoundError: If no user is found with the provided ID.
        ReadUserError: If an unexpected error occurs during database access.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(Model).where(Model.id == user_id)
                response = await session.execute(stmt)
                user_obj = response.scalars().first()

                if user_obj:
                    return UserOutput.from_orm(user_obj)
                
                else: 
                    raise UserNotFoundError(f"User with id: {user_id} not found")

    except UserNotFoundError:
        raise

    except (SQLAlchemyError, Exception) as e:
        raise ReadUserError(f"Failed to read the user with the email : {e}")


async def delete_user(user_id: uuid.UUID):
    """
    Delete a user from the database by their unique ID.

    Args:
        user_id (uuid.UUID): The unique identifier of the user to delete.

    Raises:
        ReadUserError: If the user with the given ID does not exist.
        SQLAlchemyError: If a database-related error occurs.
        Exception: For any unexpected error.

    Notes:
        - Opens an asynchronous transaction using `session.begin()`.
        - If the user exists, it is deleted within the same transaction.
        - The transaction is automatically committed or rolled back.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = select(Model).where(Model.id == user_id)
                response = await session.execute(stmt)
                user_obj = response.scalars().first()

                if not user_obj:
                    raise UserNotFoundError(f"User with id {user_id} does not exist.")

                await session.delete(user_obj)

    except (SQLAlchemyError, Exception) as e:
        raise DeleteUserError(f"Failed to delete user with id {user_id}. Original error: {e}") from e


async def if_email_exist(email : EmailStr) -> bool :
    """
    Check if an email already exists in the database.

    Args:
        email (EmailStr): The email to check.

    Returns:
        bool: True if the email exists, False otherwise.

    Raises:
        Exception: Propagates any exceptions from read_user_email.
    """
    try :
        user_output = await read_user_email(email)

        if user_output :
            return True
        
        else :
            return False
    except UserNotFoundError:
        return False
    
    except Exception as e :
        raise e
    
async def set_approved(user_id: uuid.UUID) :
    """
    Set the status of a user to 'approved'.

    This function updates the user's status in the database to indicate
    that the admin has approved the account.

    Args:
        user_id (uuid.UUID): The unique identifier of the user to approve.

    Raises:
        Exception: If updating the user's status fails.
    """
    try:
        async with AsyncSessionLocal() as session :
            async with session.begin() :
                stmt = select(Model).where(Model.id == user_id)
                response = await session.execute(stmt)
                user_obj = response.scalars().first()

                if user_obj is None :
                    raise UserNotFoundError(f"User with id {user_id} not found")

                user_obj.status = statususer.approved

    except (SQLAlchemyError, Exception) as e :
        raise Exception(f"Failed to update the status of the user {user_id}. Original error: {e}")


async def set_rejected(user_id: uuid.UUID) :
    """
    Set the status of a user to 'rejected'.

    This function updates the user's status in the database to indicate
    that the admin has rejected the account.

    Args:
        user_id (uuid.UUID): The unique identifier of the user to reject.

    Raises:
        Exception: If updating the user's status fails.
    """
    try  :
        async with AsyncSessionLocal() as session :
            async with session.begin() :
                stmt = select(Model).where(Model.id == user_id)
                response = await session.execute(stmt)
                user_obj = response.scalars().first()

                if user_obj is None :
                    raise UserNotFoundError(f"User with id {user_id} not found")

                user_obj.status = statususer.rejected

    except (SQLAlchemyError, Exception) as e :
        raise Exception(f"Failed to update the status of the user {user_id}. Original error: {e}")

