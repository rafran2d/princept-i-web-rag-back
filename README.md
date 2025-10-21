# Princept RAG Backend

Intelligent RAG-based chatbot backend for internal technical archives consultation

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

**Type**: Backend for an intelligent chatbot using RAG (Retrieval-Augmented Generation) for internal technical document consultation

This project provides a powerful backend API that enables:
- Document ingestion (PDF, DOCX)
- Intelligent text chunking and embedding
- Vector-based semantic search
- Conversational AI with context
- Real-time chat via WebSocket

---

## Features

### User Management
- User authentication and roles
- User profile management

### Chat System
- Create and manage conversations
- Message history with timestamps
- Real-time chat via WebSocket
- Message limit per chat (configurable)

### Document Ingestion
- PDF and DOCX file support
- Automatic text extraction and cleaning
- Intelligent chunking strategy:
  - Different processing for titles, tables, images
  - Smart splitting for long text
  - Context preservation with overlap
- Page limit validation
- Metadata tracking

### RAG (Retrieval-Augmented Generation)
- Vector embeddings with OpenAI
- Semantic search with pgvector
- Batch processing for performance
- Top-K document retrieval
- LLM response generation with sources

### API
- RESTful endpoints
- WebSocket support for real-time chat
- Interactive API documentation (Swagger/ReDoc)
- CORS support for frontend integration

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI (Python) |
| **Database** | PostgreSQL 14+ with pgvector |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **RAG/AI** | LlamaIndex + OpenAI |
| **Embeddings** | OpenAI text-embedding-3-small |
| **LLM** | OpenAI gpt-4o-mini |
| **Vector Search** | pgvector |
| **Server** | Uvicorn (ASGI) |

---

## Project Structure

```
princept-i-web-rag-back/
├── Backend/
│   ├── App/
│   │   ├── Controller/          # Business logic controllers
│   │   ├── Exception/           # Custom exception classes
│   │   ├── Models/              # SQLAlchemy data models
│   │   ├── Route/               # API routes/endpoints
│   │   ├── Schema/              # Pydantic validation schemas
│   │   ├── Seed/                # Database seeders
│   │   ├── Service/             # Business logic services
│   │   ├── Data/Uploads/        # Temporary file storage
│   │   ├── database.py          # Database configuration
│   │   └── main.py              # Application entry point
│   ├── Migration/               # Alembic migration scripts
│   ├── requirements.txt         # Python dependencies
│   ├── alembic.ini             # Alembic configuration
│   └── venv/                    # Virtual environment (not in git)


```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.10+ (3.10.12 recommended)
- **PostgreSQL**: 14+ with pgvector extension
- **Git**: For version control
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### Check your installations:

```bash
python3 --version    # Should show 3.10+
psql --version       # Should show PostgreSQL 14+
git --version        # Any recent version
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd princept-i-web-rag-back
```

### 2. Setup PostgreSQL Database

#### Create database and install pgvector extension:

**Option A - With psql shell:**
```bash
sudo -u postgres psql

# In psql shell:
CREATE DATABASE princept_rag_db;
\c princept_rag_db
CREATE EXTENSION IF NOT EXISTS vector;
\dx  # Verify vector extension is installed
\q
```

**Option B - Command line (if you have password):**
```bash
export PGPASSWORD="your_password"
psql -h localhost -U postgres -c "CREATE DATABASE princept_rag_db;"
psql -h localhost -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" princept_rag_db
```

### 3. Setup Python Environment

```bash
cd Backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies (this may take 2-5 minutes)
pip install -r requirements.txt
```

### 4. Create Uploads Directory

```bash
mkdir -p App/Data/Uploads
```

### 5. Configure Environment Variables

Copy the example file and edit it:

```bash
cp ../.env.example ../.env
nano ../.env
```

**Required configuration:**

```env
# OpenAI API Key - Get from https://platform.openai.com/api-keys
API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_KEY_HERE

# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=princept_rag_db
```

### 6. Run Database Migrations

```bash
# Make sure you're in Backend directory and venv is activated
alembic upgrade head
```

### 7. Seed the Database (Optional)

```bash
# Create initial user data
python -m App.Seed.UserSeed
```

---

## Configuration

Your `.env` file contains **30+ configuration variables**. Here are the key ones:

### API Configuration
```env
API_KEY=your_openai_api_key        # REQUIRED - OpenAI API key
```

### Database Configuration
```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=princept_rag_db
```

### Application Configuration
```env
APP_ENV=development                # development, staging, production

# Upload Configuration
UPLOAD_DIR=App/Data/Uploads
MAX_FILE_SIZE=10485760            # 10MB in bytes
MAX_FILES_PER_UPLOAD=3            # Maximum files per request
ALLOWED_EXTENSIONS=.pdf,.docx     # Comma-separated extensions

# Document Processing
MAX_PAGES_PER_DOCUMENT=150        # Maximum pages per document
CHUNK_SIZE=750                    # Chunk size in tokens
CHUNK_OVERLAP=75                  # Overlap between chunks
```

### Embedding Configuration
```env
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_BATCH_SIZE=100          # Batch size for embeddings
```

### LLM Configuration
```env
LLM_MODEL=gpt-4o-mini             # OpenAI model (cheaper than gpt-4)
LLM_TEMPERATURE=0.7               # Response creativity (0.0-1.0)
LLM_MAX_TOKENS=2000               # Max tokens in response
```

### Chat Configuration
```env
MAX_MESSAGES_PER_CHAT=30          # Message limit per chat
```
### JWT configuration
'''env
JWT_KEY= your_key                #For the signatures of the jwt
ALGORITHM= your_jwt_algorithm     #The creation algorithm of jwt
ACCESS_TOKEN_EXPIRES_MINUTES=15   #THe duration off an access token
REFRESH_TOKEN_EXPIRES_DAYS= 15     #The duration of a refresh token
"""

### Optional Features (commented out by default)
```env
# LLAMA_CLOUD_API_KEY=your_key    # For advanced PDF parsing
# LANGSMITH_API_KEY=your_key      # For monitoring and debugging
# SECRET_KEY=your_secret_key      # For JWT authentication
```

---

## Running the Application

### Development Mode (with auto-reload)

```bash
# Navigate to Backend directory
cd Backend

# Activate virtual environment
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# Start FastAPI development server
uvicorn App.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode (with workers)

```bash
cd Backend
source venv/bin/activate
uvicorn App.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Installation

Open your browser and navigate to:

**Health Check**: http://localhost:8000
```json
{
  "message": "Princept RAG API is running!",
  "status": "healthy"
}
```

---

## API Documentation

Once the application is running, you can access:

| Resource | URL | Description |
|----------|-----|-------------|
| **Interactive API Docs (Swagger)** | http://localhost:8000/docs | Try endpoints interactively |
| **Alternative Docs (ReDoc)** | http://localhost:8000/redoc | Clean, readable documentation |
| **OpenAPI Schema** | http://localhost:8000/openapi.json | Machine-readable API spec |

### Main Endpoints

#### Chat Management
- `POST /chat/{chat_id}/documents` - Upload documents to a chat
- `GET /chat/{chat_id}/messages` - Get conversation messages
- `POST /chat/{chat_id}/messages` -Send message

#### Health Check
- `GET /` - API health status

---

## Development

### Quick Start Commands

```bash
# Full setup from scratch
git clone <repository-url>
cd princept-i-web-rag-back

# Setup environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Install and run
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p App/Data/Uploads
alembic upgrade head
python -m App.Seed.UserSeed  # Optional
uvicorn App.main:app --reload
```

### Useful Commands

```bash
# Activate virtual environment
source Backend/venv/bin/activate

# Deactivate virtual environment
deactivate

# Run with debug logging
uvicorn App.main:app --reload --log-level debug

# Check database tables
export PGPASSWORD="your_password"
psql -h localhost -U postgres -d princept_rag_db -c "\dt"

# Reset database (CAUTION: deletes all data)
cd Backend
alembic downgrade base
alembic upgrade head
python -m App.Seed.UserSeed
```

### Running Tests

```bash
cd Backend
source venv/bin/activate

# Run tests (if you have tests)
pytest

# Run with coverage
pytest --cov=App
```

---

## Troubleshooting

### Error: "Connection refused" (PostgreSQL)

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Enable on boot
sudo systemctl enable postgresql
```

### Error: "Database does not exist"

**Solution:**
```bash
# Recreate the database
export PGPASSWORD="your_password"
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS princept_rag_db;"
psql -h localhost -U postgres -c "CREATE DATABASE princept_rag_db;"
psql -h localhost -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" princept_rag_db
```

### Error: "Invalid API key" or "Unauthorized"

**Solution:**
```bash
# Check your .env file
cat .env | grep API_KEY

# The key must start with "sk-proj-" or "sk-"
# Get a new key from https://platform.openai.com/api-keys
```

### Error: "No module named 'App'"

**Solution:**
```bash
# Make sure you're in the Backend directory
cd Backend

# Make sure venv is activated (you should see "(venv)" in your prompt)
source venv/bin/activate

# Verify Python can import App
python -c "import App; print('OK')"
```

### Error: "No such command: alembic"

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall alembic
pip install alembic
```

### Error: ModuleNotFoundError for specific packages

**Solution:**
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

### Error: "Permission denied" on Uploads directory

**Solution:**
```bash
# Fix permissions
chmod 755 Backend/App/Data/Uploads
```

### Server won't start / Port already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn App.main:app --reload --port 8001
```

---

## Data Models

### Entity Relationships

```
UserModel (users)
    ├── ChatModel (chats) [1:N]
        ├── ChatMessageModel (chat_messages) [1:N]
        └── DocumentModel (documents) [1:N]
            └── DocumentChunkModel (document_chunks) [1:N]
                └── EmbeddingModel (embeddings) [1:1]
```

### Key Models

- **UserModel**: User accounts and authentication
- **ChatModel**: Conversation sessions
- **ChatMessageModel**: Individual messages (User/LLM)
- **DocumentModel**: Uploaded documents with metadata
- **DocumentChunkModel**: Document chunks for processing
- **EmbeddingModel**: Vector embeddings for semantic search

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

If you encounter any problems:

1. Check this README's [Troubleshooting](#troubleshooting) section
2. Review the server logs for error messages
3. Verify your `.env` configuration
4. Check that PostgreSQL is running
5. Open an issue on GitHub

---

## Roadmap

- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Implement user authentication with JWT
- [ ] Add file caching for performance
- [ ] Implement pagination for messages
- [ ] Add support for more file types
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Docker support
- [ ] CI/CD pipeline

---

**Made by the Princept Team**
