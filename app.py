import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from auth import AuthError, requires_auth
from config import pagination
from models import db_drop_and_create_all, setup_db, Actor, Movie, Performance

ROWS_PER_PAGE = pagination['example']

def create_app(test_config=None):
  '''create and configure the app'''
  
  app = Flask(__name__)
  setup_db(app)
  # db_drop_and_create_all() # uncomment this if you want to start a new database on app refresh

  #============================================================#
  # API configuration
  #============================================================#

  CORS(app)
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  #============================================================#
  # Custom Functions
  #============================================================#

  def get_error_message(error, default_text):
      try:
          return error.description['message']
      except:
          return default_text

  def paginate_results(request, selection):
    # Get page from request. If not given, default to 1
    page = request.args.get('page', 1, type=int)
      
    # Calculate start and end slicing
    start =  (page - 1) * ROWS_PER_PAGE
    end = start + ROWS_PER_PAGE

      # Format selection into list of dicts and return sliced
    objects_formatted = [object_name.format() for object_name in selection]
    return objects_formatted[start:end]

  #============================================================#
  #                       API Endpoints                        #
  #============================================================#      

  #============================================================#
  # Endpoint /actors GET/POST/DELETE/UPDATE
  #============================================================#  
  @app.route('/actors', methods=['GET'])
  @requires_auth('read:actors')
  def get_actors(payload):
    selection = Actor.query.all()
    actors_paginated = paginate_results(request, selection)

    if len(actors_paginated) == 0:
      abort(404, {'message': 'No Actors found in Database!'})

    return jsonify({
      'success': True,
      'actors': actors_paginated
    })  


  @app.route('/actors', methods=['POST'])
  @requires_auth('create:actors')
  def insert_actors(payload):
    body = request.get_json()

    if not body:
      abort(400, {'message': 'Invalid JSON'})

    name   = body.get('name', None)
    age    = body.get('age', None)
    gender = body.get('gender', 'Unknown')

    if not name:
      abort(422, {'message': 'No Name'})

    if not age:
      abort(422, {'message': 'No Age'})

    # add new records and insert to DB
    new_actor = (Actor(
      name = name,
      gender = gender,
      age = age
    ))    
    new_actor.insert

    return jsonify({
      'success': True,
      'created': new_actor.id
    })

  @app.route('/actors/<actor_id>', methods=['PATCH'])
  @requires_auth('edit:actors')
  def edit_actors(payload, actor_id):
    body = request.get_json()

    if not actor_id:
      abort(400, {'message': 'Actor id not given.'})

    if not body:
      abort(400, {'message': 'Invalid JSON'})  

    # find actor
    actor_to_update = Actor.query.filter(Actor.id == actor_id).one_or_none()

    # abort if no actor with the given id
    if not actor_to_update:
      abort(404, {'message': 'Actor with id {} not found in records'.format(actor_id)})

    # extract data
    name   = body.get('name', actor_to_update.name)
    age    = body.get('age', actor_to_update.age)
    gender = body.get('gender', actor_to_update.gender)    

    # update with a new data
    actor_to_update.name = name
    actor_to_update.age = age
    actor_to_update.gender = gender
    actor_to_update.update

    return jsonify({
      'success': True,
      'updated': actor_to_update.id,
      'actor'  : [actor_to_update.format()]
    })

  @app.route('/actors/<actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actors(payload, actor_id):
    if not actor_id:
      abort(400, {'message': 'Actor ID not given'})

    # get actor by id
    actor_to_delete = Actor.query.filter(Actor.id == actor_id).one_or_none()

    if not actor_to_delete:
      abort(404, {'message': 'Actor with id {} not found in database.'.format(actor_id)})

    # delete
    actor_to_delete.delete()

    return jsonify({
      'success': True,
      'deleted': actor_id
    })


  #============================================================#
  # Endpoint /movies GET/POST/DELETE/UPDATE
  #============================================================#  
  @app.route('/movies', methods=['GET'])
  @required_auth('read:movies')
  def get_movies(payload):
    selection = Movie.query.all()
    movies_paginated = paginate_results(request, selection)

    if len(movies_paginated) == 0:
      abort(404, {'message': 'No movies found'})

    return jsonify({
      'success': True,
      'movies': movies_paginated
    })    

  @app.route('/movies', methods=['POST'])  
  @requires_auth('create:movies')
  def insert_movies(payload):
    body = request.get_json()

    if not body:
      abort(400, {'message': 'Invalid JSON'})

    # get values
    title = body.get('title', None)    
    release_date = body.get('release_date', None)

    if not title:
      abort(422, {'message': 'No Title'})

    if not release_date:
      abort(422, {'message': 'No release_date'})   

    # create a new movie record
    new_movie = (Movie(
      title = title,
      release_date = release_date
    ))  
    new_movie.insert

    return jsonify({
      'success': True,
      'created': new_movie.id
    })

  @app.route('/movies/<movie_id>', methods=['PATCH'])
  @requires_auth('edit:movies')
  def edit_movies(payload, movie_id):
    body = request.get_json()

    if not movie_id:
      abort(400, {'message': 'Movie ID Not Found'})

    if not body:
      abort(400, {'message': 'Invalid JSON'})  

    # fetch movie by ID
    movie_to_update = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if not movie_to_update:
      abort(404, {'message': 'Movie Not Found'})    

    # get records
    title = body.get('title', movie_to_update.title)
    release_date = body.get('release_date', movie_to_update.release_date)
    # update
    movie_to_update.title = title
    movie_to_update.release_date = release_date
    movie_to_update.update

    return jsonify({
      'success': True,
      'edited': movie_to_update.id,
      'movie': [movie_to_update.format()]
    })

  @app.route('/movies/<movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movies(payload, movie_id):
    if not movie_id:
      abort(400, {'message': 'Movie ID not given'})

    movie_to_delete = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if not movie_to_delete:
      abort(404, {'message': 'Movie not found'})

    movie_to_delete.delete

    return jsonify({
      'success': True,
      'deleted': movie_id
    })    


  #============================================================#
  # Error Handler Functions
  #============================================================#
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": get_error_message(error, "Bad Request")
    }), 400

  @app.errorhandler(404)
  def ressource_not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": get_error_message(error, "Resource Not Found")
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": get_error_message(error,"Unprocessable")
    }), 422  

  @app.errorhandler(AuthError)
  def authentification_failed(AuthError): 
    return jsonify({
      "success": False, 
      "error": AuthError.status_code,
      "message": AuthError.error['description']
    }), AuthError.status_code  

  return app

APP = create_app()  

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    APP.run(host='0.0.0.0', port=port, debug=True)