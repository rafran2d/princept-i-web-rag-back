from App.Exception.UserException import UserCreateError
from App.Models.UserModel import UserModel as Model
from App.Schema.UserShcema import UserInput, UserOutput
from App.database import AsyncSessionLocal
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

async def create_user(user_input: UserInput) -> UserOutput:
    try:
        hashed_password = hash_password(user_input.password)

        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_user = Model(
                    email=user_input.email,
                    display_name=user_input.display_name,
                    hashed_password=hashed_password,
                    role=user_input.role
                )
                session.add(new_user)
                await session.flush()
                await session.refresh(new_user)

        return UserOutput.from_orm(new_user)

    except SQLAlchemyError as e:
        raise UserCreateError(f"Failed to create the user {user_input.display_name}.Original error:{e}") from e
