# princept-i-web-rag-back
Developpement d’un chatbot intelligent basé sur le RAG pour la consultation d'archives techniques internes Backend

# create the .env file
copier les lignes ci-dessous dans .env et les compléter avec vos informations:

    API_KEy = 
    DB_USER = 
    DB_PASSWORD = 
    DB_HOST = 
    DB_PORT = 
    DB_NAME =  

# install backend depandencies
se deplacer dans Backend puis:

    python3 -m venv venv
    source venv/bin/activate(linux ou macos)/venv\Scripts\activate(windows)
    pip install --upgrade pip
    pip install -r requirements.txt

# perform the migration
make sur venv run then:
    alembic upgrade head