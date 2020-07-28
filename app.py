import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from auth import AuthError, requires_auth, AUTH0_DOMAIN, API_AUDIENCE, AUTH0_CALLBACK_URL, AUTH0_CLIENT_ID
from config import pagination
from models import db_drop_and_create_all, setup_db, Actor, Movie, Performance

ROWS_PER_PAGE = pagination['example']

def create_app(test_config=None):
  '''create and configure the app'''
  
  app = Flask(__name__)
  setup_db(app)
  db_drop_and_create_all()  # Uncomment - if you want to start a new database on app refresh

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
    # get from page or default page which is 1
    page = request.args.get('page', 1, type=int)
      
    # starting point and ending points
    start = (page - 1) * ROWS_PER_PAGE
    end   = start + ROWS_PER_PAGE

    formatted_data = [object_name.format() for object_name in selection]
    return formatted_data[start:end]


  @app.route("/auth")
  def generate_auth_url():
    url = f'https://{AUTH0_DOMAIN}/authorize' \
        f'?audience={API_AUDIENCE}' \
        f'&response_type=token&client_id=' \
        f'{AUTH0_CLIENT_ID}&redirect_uri=' \
        f'{AUTH0_CALLBACK_URL}'

    return jsonify({
        'auth_url': url
    })        


  #============================================================#
  #                       API Endpoints                        #
  #============================================================#    

  #============================================================#
  #                     Sample/Test Enpoint                    #
  #============================================================# 
  @app.route('/', methods=['GET'])
  def welcome():
      return jsonify({
          'Welcome': 'Working!',
          'LiveWebApp': 'https://XXXXXXX.herokuapp.com',
      })  

  #============================================================#
  # Endpoint /actors GET/POST/DELETE/UPDATE
  #============================================================#  
  @app.route('/actors', methods=['GET'])
  # @requires_auth('read:actors')
  def get_actors():
    selection = Actor.query.all()
    paginated_actors = paginate_results(request, selection)

    if len(paginated_actors) == 0:
      abort(404, {'message': 'No Actors found in Database!'})

    return jsonify({
      'success': True,
      'actors': paginated_actors
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

    if not age:
      abort(422, {'message': 'No Age'})

    if not name:
      abort(422, {'message': 'No Name'})

    # add new records and insert to DB
    new_actor = (Actor(
      name   = name,
      gender = gender,
      age    = age
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

    if not body:
      abort(400, {'message': 'Invalid JSON'})  

    if not actor_id:
      abort(400, {'message': 'Actor id not given.'})

    # find actor
    updated_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

    # abort if no actor with the given id
    if not updated_actor:
      abort(404, {'message': 'Actor with id {} not found in records'.format(actor_id)})

    # extract data
    name   = body.get('name', updated_actor.name)
    age    = body.get('age', updated_actor.age)
    gender = body.get('gender', updated_actor.gender)    

    # update with a new data
    updated_actor.name   = name
    updated_actor.age    = age
    updated_actor.gender = gender
    updated_actor.update

    return jsonify({
      'success': True,
      'updated': updated_actor.id,
      'actor'  : [updated_actor.format()]
    })

  @app.route('/actors/<actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actors(payload, actor_id):
    if not actor_id:
      abort(400, {'message': 'Actor ID not given'})

    # get actor by id
    deleted_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

    if not deleted_actor:
      abort(404, {'message': 'Actor with id {} not found in database.'.format(actor_id)})

    # delete
    deleted_actor.delete()

    return jsonify({
      'success': True,
      'deleted': actor_id
    })


  #============================================================#
  # Endpoint /movies GET/POST/DELETE/UPDATE
  #============================================================#  
  @app.route('/movies', methods=['GET'])
  @requires_auth('read:movies')
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
    new_movie.insert  # add to database

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
    edited_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if not edited_movie:
      abort(404, {'message': 'Movie Not Found'})    

    # get records
    title = body.get('title', edited_movie.title)
    release_date = body.get('release_date', edited_movie.release_date)
    # update
    edited_movie.title = title
    edited_movie.release_date = release_date
    edited_movie.update

    return jsonify({
      'success': True,
      'edited': edited_movie.id,
      'movie': [edited_movie.format()]
    })

  @app.route('/movies/<movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movies(payload, movie_id):
    if not movie_id:
      abort(400, {'message': 'Movie ID not given'})

    deleted_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

    if not deleted_movie:
      abort(404, {'message': 'Movie not found'})

    deleted_movie.delete

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
      "message": get_error_message(error, "Unprocessable")
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