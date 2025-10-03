from App.Service.UserService import create_user
from App.Exception.UserException import UserCreateError
from App.Exception.ChatException import SaveChatError
from App.Schema.UserShcema import UserInput
import asyncio


async def seed():
    try:
        user_input = {
            "email":"test123@gmail.com",
            "display_name": "Mihasiniaina",
            "password" : "raz20yol"
        }
        user_create = UserInput(**user_input)
        user_read = await create_user(user_create)

    except (UserCreateError,SaveChatError,SyntaxError,TypeError) as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(seed())