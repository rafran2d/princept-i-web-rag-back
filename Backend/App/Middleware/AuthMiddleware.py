from fastapi import FastAPI, Request,HTTPException
from App.Service.Authentification.TokenService import verify_access_token
from App.Route.ChatRoute import chat_route
from jwt import InvalidTokenError,ExpiredSignatureError
auth = FastAPI()

@chat_route.middleware("http")
async def verify_jwt_authenticity(request: Request, call_next):
    """
    Middleware to verify the authenticity of a JWT access token.

    - Checks if the 'Authorization' header exists.
    - Extracts and decodes the JWT access token.
    - Attaches the payload to `request.state.payload` for downstream routes.
    - Raises HTTPException with appropriate status codes if the token is missing,
      invalid, expired, or any unexpected error occurs.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler in the chain.

    Returns:
        Response: The response returned by the next middleware or route.

    Raises:
        HTTPException: 
            - 401 if Authorization header is missing.
            - 403 if token is invalid or expired.
            - 500 for any unexpected server error.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Typically Authorization header is in the format: "Bearer <token>"
        if auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
        else:
            access_token = auth_header

        payload = verify_access_token(access_token)
        request.state.payload = payload
        return await call_next(request)

    except (InvalidTokenError, ExpiredSignatureError) as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=403, detail=f"{type(e)}: {e}")

    except Exception as e:
        print(type(e))
        print(e)
        raise HTTPException(status_code=500, detail=f"{type(e)}: {e}")
