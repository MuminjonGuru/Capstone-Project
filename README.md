# FSND: Capstone Project - Casting Agency

## Content

1.  [Motivation]()
2.  [Project Setup]()
3.  [API Documentation]()
4.  [Authentification/Authorization]()

## Motivation

This is the final project in this course and it includes many stuff I have learned throughout the course.

1.  Database with  **postgres**  and  **sqlalchemy**  (`models.py`)
2.  API  with  **Flask**  (`app.py`)
3.  TDD  **Unittest**  (`test_app.py`)
4.  Authorization &  Authentification **Auth0**  (`auth.py`)
5.  Deployment on  `Heroku`

## Project Setup

Make sure you  `cd`  into the correct folder (with all app files) before following the setup steps. Also, you need the latest version of  [Python 3](https://www.python.org/downloads/)  and  [postgres](https://www.postgresql.org/download/)  installed on your machine.

Python 3.7
Follow instructions to install the latest version of python for your platform in the python docs

PIP Dependencies
Once you have your virtual environment setup and running, install dependencies by naviging to the /backend directory and running:
    pip install -r requirements.txt

---------

Running the server

From within the ./src directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

export FLASK_APP=app.py;
or
$env:FLASK_APP="app.py"

To run the server, execute:

flask run --reload

The --reload flag restarts the server when will happen a change on the source code.

## API Documentation

In this part you can find all the necessary info about API.

**GET** '/movies' - Retrieves all the movies in the database and represents them as JSON.

**GET** '/actors' - Gets all the actors in the database and presents them as JSON.

**POST** '/movies/create' - Will produce a new movie in the database based on the JSON that is in the body of the request.

**POST** '/actors/create'  - Create a new actor in the database based on the JSON.

**DELETE** '/movies/delete/int:movie_id' - Deletes the movie that compares to the Movie ID that is given into the URL.

**DELETE** '/actors/delete/int:actor_id' - Deletes the actor that corresponds to the Actor ID that is passed into the URL.

**UPDATE** '/actors/patch/int:actor_id' - Updates the actor that matches to the Actor ID that is given into the URL.

**UPDATE** '/movies/patch/int:movie_id'  - Updates the movie that matches to the movie ID that is given into the URL.

## Roles

Casting Assistant:
    1.  **GET**:movies
    2.  **GET**:actors    

Casting Director
    1.  **All permissions a Casting Assistant has**
    2.  **PATCH**:movie
    3.  **DELETE**:actor
    4.  **PATCH**:actor
    5.  **POST**:actor

Executive Producer
    1.  **All permissions a Casting Director has**
    2.  **DELETE**:movie
    2.  **POST**:movie

## Unit Testing

To start the tests cd into src/ then type this command in terminal

python test_app.py
