import unittest
import json
import os
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, db_drop_and_create_all, Movie, Actor, Performance
from datetime import date
from config import bearer_tokens
from sqlalchemy import desc


casting_director_auth_header = {
    'Authorization': bearer_tokens['casting_director']
}

casting_assistant_auth_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

executive_producer_auth_header = {
    'Authorization': bearer_tokens['executive_producer']
}

class AgencyTestCase(unittest.TestCase):
    def set_up(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database.path = os.environ['DATABASE_URL']
        setup_db(self.app, self.database_path)
        db_drop_and_create_all
        with self.app.app_context:
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all

    def tear_down(self):            
        pass

  #============================================================#
  # Unit Test for /actors GET method
  #============================================================#    

    def test_get_all_actors(self):
        res = self.client().get('/actors?page=1', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_error_401_get_all_actors(self):
        res = self.client().get('/actors?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_404_get_actors(self):
        res = self.client().get('/actors?page=1125125125', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'No Actor')        

  #============================================================#
  # Unit Test for /actors POST method
  #============================================================# 

    def test_create_new_actor(self):
        actor_json = {
            'name' : 'Muminjon',
            'age' : 19
        } 

        res = self.client().post('/actors', json = actor_json, headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 2)
    
    def test_error_401_new_actor(self):
        actor_json = {
            'name' : 'Muminjon',
            'age' : 19
        } 

        res = self.client().post('/actors', json = actor_json)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected.')

    def test_error_422_create_new_actor(self):
        actor_without_name = {
            'age' : 25
        } 

        res = self.client().post('/actors', json = actor_without_name, headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no name provided.')

  #============================================================#
  # Unit Test for /actors PATCH method
  #============================================================# 
  
    def test_edit_actor(self):
        update_with_new_age = {
            'age': 22
        }

        res = self.client.patch('/actors/1', json = update_with_new_age, headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actor']) > 0)
        self.assertEqual(data['updated'], 1)

    def test_error_400_edit_actor(self):
        res = self.client().patch('/actors/123412', headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Invalid Data (JSON)')

    def test_error_404_edit_actor(self):
        actor_with_new_age = {
            'age' : 25
        } 
        res = self.client().patch('/actors/321432', json = actor_with_new_age, headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Actor with id 321432 Not Found.')         
           
  #============================================================#
  # Unit Test for /actors DELETE method
  #============================================================#            

    def test_error_401_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is required')

    def test_error_403_delete_actor(self):
        res = self.client().delete('/actors/1', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission Not Found')

    def test_delete_actor(self):
        res = self.client().delete('/actors/1', headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_error_404_delete_actor(self):
        res = self.client().delete('/actors/477', headers = casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Actor with id 477 Not Found')

  #============================================================#
  # Unit Test for /movies GET method
  #============================================================#  
    def test_get_all_movies(self):
        res = self.client().get('/movies?page=1', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_error_401_get_all_movies(self):
        res = self.client().get('/movies?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is Required')

    def test_error_404_get_movies(self):    
        res = self.client().get('/movies?page=1125125125', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Not Found')

  #============================================================#
  # Unit Test for /movies POST method
  #============================================================#         
    def test_create_new_movie(self):
        movie_json = {
            'title' : 'Adventures of Muminjon',
            'release_date' : date.today()
        } 

        res = self.client().post('/movies', json = movie_json, headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 2)

    def test_error_422_create_new_movie(self):
        movie_without_name = {
            'release_date' : date.today()
        } 

        res = self.client().post('/movies', json = movie_without_name, headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Title require')  

  #============================================================#
  # Unit Test for /movies PATCH method
  #============================================================#         
    def test_edit_movie(self):        
        movie_record = {
            'release_date' : date.today()
        } 
        res = self.client().patch('/movies/1', json = movie_record, headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movie']) > 0)

    def test_error_400_edit_movie(self):
        res = self.client().patch('/movies/1', headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Invalid JSON')

    def test_error_404_edit_movie(self):    
        movie_record = {
            'release_date' : date.today()
        } 
        res = self.client().patch('/movies/32142', json = movie_record, headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Movie with id 32142 Not Found')

  #============================================================#
  # Unit Test for /movies DELETE method
  #============================================================#           
    def test_error_401_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is Required')

    def test_error_403_delete_movie(self):    
        res = self.client().delete('/movies/1', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission Not Found.')

    def test_delete_movie(self):
        res = self.client().delete('/movies/1', headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_error_404_delete_movie(self):
        res = self.client().delete('/movies/477', headers = executive_producer_auth_header) 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'] , 'Movie with id 477 not found in database.')


if __name__ == "__main__":
    unittest.main()        