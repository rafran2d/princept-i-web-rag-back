from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from App.Service.Authentification.TokenService import verify_access_token
from App.Route.ChatRoute import chat_route
from App.Route.AuthRoute import auth_route
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()
REFRESH_TOKEN_EXPIRES_AT = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS"))

app = FastAPI(
    title="Princept RAG API",
    description="Intelligent RAG-based chatbot backend for internal technical archives consultation",
    version="1.0.0"
)

origins = [
    "http://localhost:3001",
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def verify_jwt_authenticity(request: Request, call_next):
    public_paths = ["/", "/docs", "/openapi.json", "/redoc"]
    
    if request.url.path in public_paths or request.url.path.startswith("/auth"):
        return await call_next(request)
    
    if request.url.path.startswith("/chat"):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing"}
            )
        
        try:
            if not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token format invalid. Must start with 'Bearer '"}
                )
            
            access_token = auth_header.split(" ")[1]
            
            if not access_token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token is empty after extraction"}
                )
            
            payload = verify_access_token(access_token)
            request.state.payload = payload
            
        except ExpiredSignatureError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"ExpiredSignatureError: {str(e)}"}
            )
        except InvalidTokenError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"InvalidTokenError: {str(e)}"}
            )
        except Exception as e:
            print(f"Erreur inattendue dans le middleware: {type(e).__name__}: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal Server Error: {type(e).__name__}"}
            )
    
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