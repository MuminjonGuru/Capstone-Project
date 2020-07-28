import os
SECRET_KEY = os.urandom(32)

basedir = os.path.abspath(os.path.dirname(__file__))

auth0_config = {
    "AUTH0_DOMAIN": "dev-m-guru.auth0.com",
    "ALGORITHMS": "RS256",
    "API_AUDIENCE": "http://127.0.0.1:5000/",
    "AUTH0_CLIENT_ID": "0wMjUCi4MrsgFoEt1seV1XcTLHc8Yl6h",
    "AUTH0_CALLBACK_URL": "http://localhost:5000"
}

pagination = {
    "example": 10  # Limits returned rows of API
}

bearer_tokens = {
    "casting_assistant": "Bearer <token>",
    "executive_producer": "Bearer <token>",
    "casting_director": "Bearer <token>"
}

database_setup = {
    "database_name_production": "FSND_Capstone",
    "user_name": "postgres",  # default
    "password": "su",
    "port": "localhost:5432"  # default
}
