import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'root', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.VALID_NEW_QUESTION = {
            'question': 'Which is the test framework used in this project?',
            'answer': 'unittest',
            'category': '1',
            'difficulty': 3
        }

        self.INVALID_QUESTION = {
            'question': '',
            'answer': '',
            'category': '5',
            'difficulty': 4
        }

        self.VALID_SEARCH_BODY = {
            'searchTerm': 'w',
            'currentCategory': '1'
        }

        self.INVALID_SEARCH_BODY = {
            'search_term': 'what'
        }

        self.VALID_PLAY_QUIZ_BODY = {
            'previous_questions': [1, 2],
            'quiz_category': {
                'id': '1'
            }
        }

        self.INVALID_PLAY_QUIZ_BODY = {
            'previous_questions': [1, 2]
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_health(self):
        """Test for GET / (health endpoint)"""
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('health', data)
        self.assertEqual(data['health'], 'Running!!')

    def test_get_categories(self):
        """Passing Test for GET /categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertIn('categories', data)

    def test_get_questions(self):
        """Passing Test for GET /questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertIn('categories', data)
        self.assertTrue(data['categories'])
        self.assertIn('current_category', data)
        self.assertIsNone(data['current_category'])
        self.assertIn('total_questions', data)
        self.assertTrue(len(data['questions']))

    def test_404_get_questions(self):
        """Failing Test for GET /questions, page number out of bound"""
        res = self.client().get('/questions?page=23')

        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        """Passing Test for DELETE /questions/<question_id>"""
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data)
        self.assertTrue(data['success'])

    def test_404_delete_question(self):
        """Failing Test for DELETE /questions/<question_id>, question id does not exist"""
        res = self.client().delete('/questions/3000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertIn('success', data)
        self.assertFalse(data['success'])

    def test_create_question(self):
        """Passing Test for POST /questions"""
        res = self.client().post('/questions', json=self.VALID_NEW_QUESTION)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertIn('success', data)
        self.assertTrue(data['success'])

    def test_422_create_question(self):
        """Failing Test for POST /questions, required fields empty"""
        res = self.client().post('/questions', json=self.INVALID_QUESTION)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertIn('success', data)
        self.assertFalse(data['success'])

    def test_search_questions(self):
        """Passing Test for POST /questions/search"""
        res = self.client().post('/questions/search', json=self.VALID_SEARCH_BODY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('current_category', data)
        self.assertEqual(data['current_category'], self.VALID_SEARCH_BODY['currentCategory'])
        self.assertIn('search_term', data)
        self.assertEqual(data['search_term'], self.VALID_SEARCH_BODY['searchTerm'])
        self.assertTrue(len(data['questions']))

    def test_400_search_questions(self):
        """Failing Test for POST /questions/search, missing required fields"""
        res = self.client().post('/questions/search', json=self.INVALID_SEARCH_BODY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertIn('success', data)
        self.assertFalse(data['success'])

    def test_category_specific_questions(self):
        """Passing Test for GET /categories/<category_id>/questions"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertIn('categories', data)
        self.assertIn('current_category', data)
        self.assertEqual(data['current_category'], '1')
        self.assertIn('total_questions', data)
        self.assertTrue(len(data['questions']))

    def test_404_category_specific_questions(self):
        """Failing Test for GET /categories/<category_id>/questions, invalid category id"""
        res = self.client().get('/categories/23/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertIn('success', data)
        self.assertFalse(data['success'])

    def test_play_quizzes(self):
        """Passing Test for POST /quizzes"""
        res = self.client().post("/quizzes", json=self.VALID_PLAY_QUIZ_BODY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('question', data)
        self.assertEqual(str(data['question']['category']), self.VALID_PLAY_QUIZ_BODY['quiz_category']['id'])
        self.assertTrue(data['question'])

    def test_404_play_quizzes(self):
        """Failing Test for POST /quizzes, missing required fields"""
        res = self.client().post("/quizzes", json=self.INVALID_PLAY_QUIZ_BODY)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertIn('success', data)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
