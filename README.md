# princept-i-web-rag-back

Intelligent RAG-based chatbot backend for internal technical archives consultation

## Project Overview

**Type**: Backend for an intelligent chatbot using RAG (Retrieval-Augmented Generation) for internal technical document consultation

### Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector for embeddings
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic
- **RAG/AI**: LlamaIndex + OpenAI

## Project Structure

```
Backend/
├── App/
│   ├── Models/          # SQLAlchemy data models
│   ├── Controller/      # Business logic controllers
│   ├── Route/          # API routes/endpoints
│   ├── Service/        # Services (document ingestion)
│   ├── Data/           # Temporary upload storage
│   ├── Test/           # Tests
│   ├── database.py     # Database configuration
│   └── main.py         # Entry point
├── Migration/          # Alembic migration scripts
└── requirements.txt    # Python dependencies
```

## Data Models

**Main relationships**:
- `UserModel` → `ChatModel` (1:N)
- `ChatModel` → `DocumentModel` + `ChatMessageModel` (1:N)
- `DocumentModel` → `DocumentChunkModel` (1:N)
- Embedding support with `EmbeddingModel`

## Key Features

1. **User Management**: Authentication, roles
2. **Chat System**: Conversations with history
3. **Document Ingestion**: PDF/DOCX support with intelligent chunking
4. **RAG**: Vector embedding and search
5. **API**: FastAPI endpoints for frontend integration

## Technical Highlights

- **Sophisticated Chunking**: Different processing for content types (titles, tables, images)
- **Automatic Text Cleaning**: Text normalization and preprocessing
- **Metadata Preservation**: Page information and file type tracking
- **Async Architecture**: Non-blocking operations with AsyncSession

## Setup

### Prerequisites
- Python 3.12+ (recommended to use pyenv for version management)
- PostgreSQL with pgvector extension
- Git

### Install Python 3.12 with pyenv (recommended)
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell configuration
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.12.7
pyenv install 3.12.7
pyenv local 3.12.7  # Set for this project
```

### Create .env file
Copy the example file and fill with your information:

```bash
cp .env.example .env
# Then edit .env with your actual credentials
```

Or manually create .env with:
```
API_KEY=your_openai_api_key_here
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=princept_rag_db
```

### Install backend dependencies
Navigate to Backend directory then:

```bash
cd Backend

# Create virtual environment with Python 3.12
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install alembic asyncpg uvicorn  # Additional required packages
```

### Database setup
Make sure PostgreSQL is running and create the database:

```bash
# Create database and install pgvector extension
createdb princept_rag_db
psql -d princept_rag_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Or using psql directly:
# psql -U postgres -h localhost
# CREATE DATABASE princept_rag_db;
# \c princept_rag_db
# CREATE EXTENSION IF NOT EXISTS vector;
```

Run database migrations:
```bash
# Make sure you're in Backend directory and venv is activated
cd Backend
source venv/bin/activate
alembic upgrade head
```

## Running the Application

### Development Mode
```bash
# Navigate to Backend directory
cd Backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Start FastAPI development server
uvicorn App.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
cd Backend
source venv/bin/activate
uvicorn App.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

Once running, the API will be available at:
- **Main API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Interactive API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Quick Start Commands

```bash
# Clone and setup
git clone <repository-url>
cd princept-i-web-rag-back

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Install and run
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install alembic asyncpg uvicorn
alembic upgrade head
uvicorn App.main:app --reload
```