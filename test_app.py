import unittest
import os
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, db_drop_and_create_all, Movie, Actor, Performance
from datetime import date
from config import bearer_tokens
from sqlalchemy import desc

# Tokens to Test the Unit Tests
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
    def initialize_the_setup(self):
        self.app = create_app
        self.client = self.app.test_client
        self.database.path = os.environ['DATABASE_URL']

        setup_db(self.app, self.database_path)
        db_drop_and_create_all

        with self.app.app_context:
            self.db = SQLAlchemy
            self.db.init_app(self.app)
            self.db.create_all

    def fracture(self):
        pass

    """
    Unit Test for /actors GET function
    """

    def test_try_to_get_all_actors(self):
        response = self.client().get(
            '/actors?page=1',
            headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertTrue(len(records['actors']) > 0)

    def test_error_401_get_all_actors_by_page(self):
        response = self.client().get('/actors?page=1')
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Authorization Header is Required')

    def test_error_404_get_actors_by_page(self):
        response = self.client().get(
            '/actors?page=3',
            headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Actor not Found')

    """
    Unit Test for /actors POST function
    """

    def test_create_new_actor_with_all_data(self):
        actor_json = {
            'name': 'Muminjon',
            'age': 19
        }

        response = self.client().post('/actors', json=actor_json,
                                      headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertEqual(records['created'], 2)

    def test_error_401_new_actor(self):
        actor_json = {
            'name': 'Muminjon',
            'age': 19
        }

        response = self.client().post('/actors', json=actor_json)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Authorization Header is Required.')

    def test_error_422_create_new_actor(self):
        actor_without_name = {
            'age': 25
        }

        response = self.client().post(
            '/actors',
            json=actor_without_name,
            headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Name is Not Provided.')

    """
    Unit Test for /actors PATCH function
    """

    def test__try_to_edit_actor(self):
        update_with_new_age = {
            'age': 22
        }

        response = self.client.patch(
            '/actors/1',
            json=update_with_new_age,
            headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertTrue(len(records['actor']) > 0)
        self.assertEqual(records['updated'], 1)

    def test_error_400_edit_actor(self):
        response = self.client().patch(
            '/actors/2001', headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Invalid Data (JSON)')

    def test_error_404_edit_actor_with_unknown_id(self):
        actor_with_new_age = {
            'age': 25
        }
        response = self.client().patch(
            '/actors/20010224',
            json=actor_with_new_age,
            headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Actor with id 20010224 Not Found.')

    """
    Unit Test for /actors DELETE function
    """

    def test_error_401_delete_actor(self):
        response = self.client().delete('/actors/1')
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Authorization Header is Required')

    def test_error_403_try_delete_actor_without_permission(self):
        response = self.client().delete(
            '/actors/1', headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Permission Not Found')

    def test_delete_actor(self):
        response = self.client().delete('/actors/1',
                                        headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertEqual(records['deleted'], '1')

    def test_error_404_delete_actor(self):
        response = self.client().delete(
            '/actors/477', headers=casting_director_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Actor with id 477 Not Found')

    """
    Unit Test for /movies GET function
    """

    def test_get_all_movies(self):
        response = self.client().get(
            '/movies?page=1',
            headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertTrue(len(records['movies']) > 0)

    def test_error_401_get_all_movies(self):
        response = self.client().get('/movies?page=1')
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Authorization Header is Required')

    def test_error_404_get_movies_by_page(self):
        response = self.client().get(
            '/movies?page=24022001',
            headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Not Found')

    """
    Unit Test for /movies POST function
    """

    def test_create_new_movie(self):
        movie_json = {
            'title': 'Adventures of Muminjon',
            'release_date': date.today()
        }

        response = self.client().post('/movies', json=movie_json,
                                      headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertEqual(records['created'], 2)

    def test_error_422_create_new_movie_without_title(self):
        movie_without_name = {
            'release_date': date.today()
        }

        response = self.client().post('/movies', json=movie_without_name,
                                      headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Title required.')

    """
    Unit Test for /movies PATCH function
    """

    def test_try_to_edit_movie(self):
        movie_record = {
            'release_date': date.today()
        }
        response = self.client().patch('/movies/1', json=movie_record,
                                       headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertTrue(len(records['movie']) > 0)

    def test_error_400_edit_movie(self):
        response = self.client().patch('/movies/1',
                                       headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Invalid JSON')

    def test_error_404_edit_movie_by_id(self):
        movie_record = {
            'release_date': date.today()
        }
        response = self.client().patch(
            '/movies/199121',
            json=movie_record,
            headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Movie with id 199121 Not Found')

    """
    Unit Test for /movies DELETE function
    """

    def test_error_401_try_delete_movie(self):
        response = self.client().delete('/movies/1')
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Authorization Header is Required')

    def test_error_403_delete_movie(self):
        response = self.client().delete(
            '/movies/1', headers=casting_assistant_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(records['success'])
        self.assertEqual(records['message'], 'Permission Not Found.')

    def test_delete_movie_by_id(self):
        response = self.client().delete(
            '/movies/1', headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records['success'])
        self.assertEqual(records['deleted'], '1')

    def test_error_404_delete_movie(self):
        response = self.client().delete(
            '/movies/477', headers=executive_producer_auth_header)
        records = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(records['success'])
        self.assertEqual(
            records['message'],
            'Movie with id 477 not found in database.')


if __name__ == "__main__":
    unittest.main()
