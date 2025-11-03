from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from App.Service.Authentification.TokenService import verify_access_token
from App.Route.ChatRoute import chat_route
from App.Route.AuthRoute import auth_route
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
REFRESH_TOKEN_EXPIRES_AT = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS"))

app = FastAPI(
    title="Princept RAG API",
    description="Intelligent RAG-based chatbot backend for internal technical archives consultation",
    version="1.0.0"
)

# Custom CORS middleware for development - allows all origins with credentials
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Get requested headers for preflight
        requested_headers = request.headers.get("access-control-request-headers", "*")

        if request.method == "OPTIONS":
            response = JSONResponse(content={}, status_code=200)
            # Set CORS headers for preflight
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                response.headers["Access-Control-Allow-Origin"] = "*"

            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = requested_headers
            response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
            return response

        # For actual requests
        response = await call_next(request)

        # Allow the requesting origin (whatever it is)
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = requested_headers

        return response

app.add_middleware(CustomCORSMiddleware)

@app.middleware("http")
async def verify_jwt_authenticity(request: Request, call_next):
    public_paths = ["/", "/docs", "/openapi.json", "/redoc"]

    # Allow OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path in public_paths or request.url.path.startswith("/auth"):
        return await call_next(request)

    if request.url.path.startswith("/chat"):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            response = JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing"}
            )
            # Add CORS headers
            origin = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        
        try:
            if not auth_header.startswith("Bearer "):
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Token format invalid. Must start with 'Bearer '"}
                )
                origin = request.headers.get("origin", "*")
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                return response

            access_token = auth_header.split(" ")[1]

            if not access_token:
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Token is empty after extraction"}
                )
                origin = request.headers.get("origin", "*")
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                return response

            payload = verify_access_token(access_token)
            request.state.payload = payload

        except ExpiredSignatureError as e:
            response = JSONResponse(
                status_code=401,
                content={"detail": f"ExpiredSignatureError: {str(e)}"}
            )
            origin = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        except InvalidTokenError as e:
            response = JSONResponse(
                status_code=401,
                content={"detail": f"InvalidTokenError: {str(e)}"}
            )
            origin = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        except Exception as e:
            print(f"Erreur inattendue dans le middleware: {type(e).__name__}: {e}")
            response = JSONResponse(
                status_code=500,
                content={"detail": f"Internal Server Error: {type(e).__name__}"}
            )
            origin = request.headers.get("origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
    
    return await call_next(request)

app.include_router(auth_route)
app.include_router(chat_route)

@app.get("/")
async def root():
    return {
        "message": "Princept RAG API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )