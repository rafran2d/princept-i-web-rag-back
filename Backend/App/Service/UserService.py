from App.Exception.UserException import UserCreateError
from App.Models.UserModel import UserModel as Model
from App.Schema.UserShcema import UserInput, UserOutput
from App.database import AsyncSessionLocal
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

def hash_password(password: str) -> str :
    """
    Hash a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password as a UTF-8 string.
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #create the hashed password
    return hashed_password.decode('utf-8') #convert the hashed passowrd as a string

async def create_user(user_input: UserInput) -> UserOutput :
    """
    Create a new user in the database with a hashed password.

    Args:
        user_input (UserInput): Pydantic model containing user data (email, display_name, password, role).

    Returns:
        UserOutput: Pydantic model representing the newly created user.

    Raises:
        UserCreateError: If the user cannot be created due to a database error.
    """
    try:
        hashed_password = hash_password(user_input.password)

        async with AsyncSessionLocal() as session :  #start communication with the db 
            async with session.begin() : #start the conversation
                new_user = Model(
                    email=user_input.email,
                    display_name=user_input.display_name,
                    hashed_password=hashed_password,
                    role=user_input.role
                )
                session.add(new_user)
                await session.flush() #send the modification without commiting yet

        return UserOutput.from_orm(new_user)

    except SQLAlchemyError as e :
        raise UserCreateError(f"Failed to create the user {user_input.display_name}.Original error:{e}") from e
