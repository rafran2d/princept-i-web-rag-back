from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request,HTTPException
from App.Service.UserService import read_user_id
from App.Service.Authentification.TokenService import(
    verify_access_token,
    hash_token,
    read_refresh_token,
    set_revoked_token,
    generate_refresh_token,
    generate_access_token,
    create_refresh_token
    )
from App.Schema.RefreshTokenSchema import RefreshTokenInput
from App.Route.ChatRoute import chat_route
from .Route.AuthRoute import auth_route
from jwt import InvalidTokenError,ExpiredSignatureError
from .Route.AuthRoute import auth_route
from App.Exception.TokenException import (
    TokenRevokedError,
    TokenNotFoundError
)
from dotenv import load_dotenv
import os

load_dotenv()

REFRESH_TOKEN_EXPIRES_AT  = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS"))


app = FastAPI(
    title="Princept RAG API",
    description="Intelligent RAG-based chatbot backend for internal technical archives consultation",
    version="1.0.0"
)

@app.middleware("http")
async def verify_jwt_authenticity(request: Request, call_next):
    if request.url.path.startswith("/chat"):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        access_token = None

        try:
            if auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1] 
            else:
                raise InvalidTokenError("Token format invalid. Must start with 'Bearer '")

            if not access_token:
                 raise InvalidTokenError("Token is empty after extraction.")

            payload = verify_access_token(access_token)
            request.state.payload = payload
        

        except ExpiredSignatureError:
            refresh_token = request.cookies.get("refresh_token")

            if not refresh_token:
                raise TokenNotFoundError("No refresh token was saved in the cookie")
            
            hashed_token = hash_token(refresh_token)
            refresh_token_obj = await read_refresh_token(hashed_token)
            await set_revoked_token(refresh_token_obj.id)
            if hashed_token == refresh_token_obj.hashed_token :
                if not refresh_token_obj.revoked :

                    user_output = await read_user_id(refresh_token_obj.user_id)
                    new_access_token = generate_access_token(user_output)
                    new_refresh_token = generate_refresh_token()
                    refresh_token_input = RefreshTokenInput(
                        user_id= refresh_token_obj.user_id,
                        token=new_refresh_token
                    )
                    await create_refresh_token(refresh_token_input)

                    response = JSONResponse(status_code=200,content={"acess_token" : new_access_token})
                    response .set_cookie(
                        key="refresh_token",
                        value= new_refresh_token,
                        max_age= REFRESH_TOKEN_EXPIRES_AT * 24 * 60 * 60,
                        httponly=True,
                        secure=True,
                        samesite='strict'
                
                    )

                    return response
                
                else :
                    raise TokenRevokedError(f"The token: {refresh_token_obj.id} is already revoked")

            else :
                raise TokenNotFoundError(f"The token: {refresh_token_obj} is not from the application")


        except InvalidTokenError as e:
            raise HTTPException(status_code=403, detail=f"{type(e).__name__}: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {type(e).__name__}: {e}")
        
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_route)
app.include_router(auth_route)

@app.get("/")
async def root():
    return {"message": "Princept RAG API is running!", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)