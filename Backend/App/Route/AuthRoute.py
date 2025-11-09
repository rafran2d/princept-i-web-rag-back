from App.Service.UserService import (
    create_user,
    compare_passwd,
    read_user_id,
    set_rejected,
    set_approved,
    read_registers,
    create_user_admin
)
from App.Service.Authentification.TokenService import (
    generate_access_token,
    generate_refresh_token,
    create_refresh_token,
    hash_token,
    set_revoked_token,
    read_refresh_token
)
from App.Schema.UserShcema import UserOutput,UserExternalInput,UserExternalInputSG,statususer
from App.Schema.RefreshTokenSchema import RefreshTokenInput
from App.Schema.AuthRouteSchema import Sign_upoutput
from App.Exception.UserException import (
    EmailAlreadyUsedError,
    EmailStructError,
    IncorrectPasswordError,
    UserNotFoundError
)
from App.Exception.TokenException import (
    TokenRevokedError,
    TokenNotFoundError
)
from fastapi import APIRouter,HTTPException,Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

REFRESH_TOKEN_EXPIRES_AT  = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS"))

auth_route = APIRouter(
    prefix="/auth",
    tags=['auth']
)

@auth_route.post("/sign_up",response_model=Sign_upoutput )
async def sign_up(User : UserExternalInputSG) :
    """
    Handle user registration.

    This endpoint creates a new user based on the provided input data.
    Returns a success message and the created user object upon successful registration.

    Args:
        User (UserInput): User data containing email and password.

    Returns:
        Sign_upoutput: The response containing the status code, created user, and success message.
        JSONResponse: Contains a message informing that the Email is already used or the email is invalid

    Raises:
        HTTPException: If the email is already used, invalid, or an unexpected error occurs.
    """
    try:
        user_rseponse : UserOutput =  await create_user(User)

        return Sign_upoutput(
            status_code= 201,
            data= user_rseponse,
            message= "User created successfuly"
        )

    except EmailAlreadyUsedError as e :
        return JSONResponse(status_code=200,content={"message":"Email already used"})
    
    except EmailStructError as e :
        return JSONResponse(status_code=200, content={"message":"Invalid Email"})
    
    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))
    
@auth_route.post("/sign_up/admin",response_model=Sign_upoutput )
async def sign_up(User : UserExternalInputSG) :
    """
    Handle user registration.

    This endpoint creates a new user based on the provided input data.
    Returns a success message and the created user object upon successful registration.

    Args:
        User (UserInput): User data containing email and password.

    Returns:
        Sign_upoutput: The response containing the status code, created user, and success message.
        JSONResponse: Contains a message informing that the Email is already used or the email is invalid

    Raises:
        HTTPException: If the email is already used, invalid, or an unexpected error occurs.
    """
    try:
        user_rseponse : UserOutput =  await create_user_admin(User)

        return Sign_upoutput(
            status_code= 201,
            data= user_rseponse,
            message= "User created successfuly"
        )

    except EmailAlreadyUsedError as e :
        return JSONResponse(status_code=200,content={"message":"Email already used"})
    
    except EmailStructError as e :
        return JSONResponse(status_code=200, content={"message":"Invalid Email"})
    
    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))
    


@auth_route.patch("/approve/{user_id}")
async def approve_user(user_id: uuid.UUID):
    """
    Approve a user by setting their status to 'approved'.

    This endpoint is typically used by an admin to approve a user's registration.
    The user's status is updated in the database. 

    Args:
        user_id (uuid.UUID): The unique identifier of the user to approve.

    Returns:
        JSONResponse: A JSON message confirming the successful update.

    Raises:
        HTTPException 404: If the user with the given ID does not exist.
        HTTPException 500: If any other error occurs during the update process.
    """
    try:
        await set_approved(user_id)
        return JSONResponse(
            status_code=200,
            content={"message": "Update successful"}
        )
    except UserNotFoundError as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=404, detail=str(type(e)) + ": " + str(e))
    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))


@auth_route.patch("/rejecte/{user_id}")
async def reject_user(user_id: uuid.UUID):
    """
    Reject a user by setting their status to 'rejected'.

    This endpoint is typically used by an admin to reject a user's registration.
    The user's status is updated in the database.

    Args:
        user_id (uuid.UUID): The unique identifier of the user to reject.

    Returns:
        JSONResponse: A JSON message confirming the successful update.

    Raises:
        HTTPException 404: If the user with the given ID does not exist.
        HTTPException 500: If any other error occurs during the update process.
    """
    try:
        await set_rejected(user_id)
        return JSONResponse(
            status_code=200,
            content={"message": "Update successful"}
        )
    except UserNotFoundError as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=404, detail=str(type(e)) + ": " + str(e))
    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))

@auth_route.post("/login")
async def login(User : UserExternalInput) :
    """
    Handle user login and token generation.

    This endpoint validates user credentials, generates an access token and a refresh token,
    and sets the refresh token in a secure HttpOnly cookie.

    Args:
        User (UserInput): User credentials containing email and password.

    Returns:
        JSONResponse: Contains the access token in the response body and the refresh token as a cookie.
        JSONResposne: Contains a message informing that the user was not found
        JSONResponse: Contains a message informing that the pasword is incorrect
        JSONResponse: Contains a messag infoming that the email structrur is invalid

    Raises:
        HTTPException: If unexpected error occurs.
    """
    try:
        if_correct,user_output = await compare_passwd(User)

        if if_correct :
            if user_output.status == statususer.pending:    
                return JSONResponse(status_code=200,content={"message":"This user is pending"})
            elif user_output.status == statususer.rejected:
                return JSONResponse(status_code=200,content={"message":"This user is rejected"})
            else:
                access_token = generate_access_token(user_output)
                refresh_token = generate_refresh_token()
                refresh_token_input = RefreshTokenInput(
                    user_id= user_output.id,
                    token= refresh_token
                )

                await create_refresh_token(refresh_token_input)

                response = JSONResponse(status_code=200,content={"message":"Login successful",
                    "access_token" : access_token})
                response .set_cookie(
                    key="refresh_token",
                    value= refresh_token,
                    max_age= REFRESH_TOKEN_EXPIRES_AT * 24 * 60 * 60,
                    httponly=True,
                    secure=False,
                    samesite="lax",
                    path="/"
                )

                return response

    except UserNotFoundError as e :
        res = JSONResponse(status_code=200, content={"message":"User Not Found"})
        return res

    except IncorrectPasswordError as e :
        res = JSONResponse(status_code=200,content={"message":"Incorrect Password"})
        return res

    except EmailStructError as e :
        res = JSONResponse(status_code=200, content={"message":"Invalid Email"})
        return res
    
    except Exception as e :
        print(type(e))
        print(e)
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))


@auth_route.patch("/logout")
async def revoked_refresh_token(request : Request) :
    """
    Handle user logout by revoking the refresh token.

    This endpoint marks the latest refresh token as revoked in the database
    and removes it from the user's cookies.

    Args:
        request (Request): The HTTP request object.

    Returns:
        JSONResponse: A success message indicating the user has been logged out.

    Raises:
        HTTPException: If an unexpected error occurs during the logout process.
    """
    try :
        refresh_token = request.cookies.get("refresh_token")
        hashed_token = hash_token(refresh_token)
        refresh_token_obj = await read_refresh_token(hashed_token)
        await set_revoked_token(refresh_token_obj.id)

        response = JSONResponse(status_code=200,content={"detail" : "log out sucessful"})
        response.delete_cookie("refresh_token")

        return response
    
    except Exception as e :
        print(type(e))
        print(e)
        raise HTTPException(status_code=500,detail=str(type(e))+": "+ str(e))


@auth_route.post('/refresh')
async def refresh_access_token(request: Request):
    """
    Refresh the user's access token using a valid refresh token stored in cookies.

    This endpoint verifies the validity of the refresh token, revokes the old one, 
    generates new access and refresh tokens, and updates the database accordingly. 
    The new refresh token is stored as an HTTP-only cookie.

    Args:
        request (Request): The incoming HTTP request containing cookies.

    Returns:
        JSONResponse: A response containing a new access token and a success message.

    Raises:
        TokenNotFoundError: If no refresh token is found in cookies or if the token is invalid.
        TokenRevokedError: If the refresh token has already been revoked.
        HTTPException: If an unexpected error occurs during the refresh process.
    """
    try:
        refresh_token = request.cookies.get("refresh_token")
        print(f"Cookies reçus: {request.cookies}")  

        if not refresh_token:
            raise TokenNotFoundError("No refresh token was saved in the cookie")
        
        hashed_token = hash_token(refresh_token)
        refresh_token_obj = await read_refresh_token(hashed_token)

        if refresh_token_obj.revoked:
            raise TokenRevokedError(f"The token: {refresh_token_obj.id} is already revoked")

        if hashed_token != refresh_token_obj.hashed_token:
            raise TokenNotFoundError("The token is not from the application")

        await set_revoked_token(refresh_token_obj.id)

        user_output = await read_user_id(refresh_token_obj.user_id)
        new_access_token = generate_access_token(user_output)
        new_refresh_token = generate_refresh_token()
        
        refresh_token_input = RefreshTokenInput(
            user_id=refresh_token_obj.user_id,
            token=new_refresh_token
        )
        await create_refresh_token(refresh_token_input)

        response = JSONResponse(
            status_code=200,
            content={
                "access_token": new_access_token,  
                "message": "refresh_tokens successful"
            }
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=REFRESH_TOKEN_EXPIRES_AT * 24 * 60 * 60,
            httponly=True,
            secure=False,
            samesite='lax',
            path="/"
        )

        return response

    except (TokenNotFoundError, TokenRevokedError) as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=401, detail=str(type(e)) + ": " + str(e))
    
    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))


@auth_route.get("/registers")
async def get_registers(request: Request):
    """
    Retrieve all users with a 'pending' status from the database.

    This endpoint is typically used by administrators to view users who have 
    registered but whose accounts are not yet approved or activated.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        JSONResponse: 
            - 200 OK with a list of pending users if any exist.
            - 200 OK with an empty list if no pending users are found.

    Raises:
        HTTPException: If an error occurs while retrieving the pending users.
    """
    try:
        registers: list[UserOutput] | None = await read_registers()

        return registers or []

    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=str(type(e)) + ": " + str(e))
