import os
SECRET_KEY = os.urandom(32)

basedir = os.path.abspath(os.path.dirname(__file__))

auth0_config = {
    "AUTH0_DOMAIN" : "_.eu.auth0.com",
    "ALGORITHMS" : ["RS256"],
    "API_AUDIENCE" : ""
}

pagination = {
    "example" : 10 # Limits returned rows of API
}

bearer_tokens = {
    "casting_assistant" : "Bearer <token>",
    "executive_producer" : "Bearer <token>",
    "casting_director" : "Bearer <token>"
}

database_setup = {
   "database_name_production": "agency",
   "user_name": "postgres", # default
   "password": "test2020",
   "port" : "localhost:5432" # default
}