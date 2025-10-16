from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .Route.ChatRoute import chat_route
from .Route.AuthRoute import auth_route

app = FastAPI(
    title="Princept RAG API",
    description="Intelligent RAG-based chatbot backend for internal technical archives consultation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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