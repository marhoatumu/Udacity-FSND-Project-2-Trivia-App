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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
            )

        self.new_question = {
                        "question": "Who wrote the novel Anansi Boys?", 
                        "answer": "Neil Gaiman", 
                        "difficulty": 3,
                        "category": 4
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #Test for paginated display of books after GET request
    def test_get_paginated_questions(self):
      res = self.client().get('/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(data['categories'])
      self.assertTrue(len(data['questions']))

    #Test for failed paginated display of books after GET request
    def test_404_requesting_beyond_valid_question_page(self):
      res = self.client().get('/questions?page=1000', json={'category': 1})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Not found')

    #Test for paginated display of categories after GET request
    def test_get_paginated_categories(self):
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['categories'])
      self.assertTrue(data['total_categories'])

    #Test for failed paginated display of categories after GET request
    def test_404_requesting_beyond_valid_category_page(self):
      res = self.client().get('/categories?page=1000')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Not found')

    #Test for deleting questions
    # def test_delete_question(self):
    #   res = self.client().delete('/questions/10')
    #   data = json.loads(res.data)
    #   question = Question.query.filter(Question.id == 10).one_or_none()

    #   self.assertEqual(res.status_code, 200)
    #   self.assertEqual(data['success'], True)
    #   self.assertTrue(data['deleted'], 10)
    #   self.assertTrue(data['total_questions'])
    #   self.assertTrue(len(data['questions']))
    #   self.assertEqual(question, None)

    #Test for failed question deletion
    def test_422_delete_question_that_doesnt_exist(self):
      res = self.client().delete('/questions/1000')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Request could not be processed')

    #Test for creating questions
    def test_create_question(self):
      res = self.client().post('/questions', json=self.new_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['created'])
      self.assertTrue(len(data['questions']))

    #Test for failed question creation
    def test_405_if_question_creation_not_allowed(self):
      res = self.client().post('/questions/15000', json=self.new_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Method not allowed')   

    #Test for successful question search
    def test_get_question_search_with_results(self):
      search = {'searchTerm': 'title', }
      res = self.client().post('questions/search', json=search)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])

    #Test for failed question search
    def test_get_question_search_without_results(self):
      search = {'searchTerm': 'Financlge', }
      res = self.client().post('questions/search', json=search)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertEqual(data['total_questions'], 0)
      self.assertEqual(len(data['questions']), 0)

    #Test for successfully listing questions by category
    def test_get_questions_by_category(self):
      res = self.client().get('/categories/4/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertNotEqual(len(data['questions']), 4)
      self.assertEqual(data['current_category'], 4)

    #Test for listing questions by a category that doesn't exist
    def test_questions_in_category_not_found(self):
      res = self.client().get('/categories/100/questions')

      data = json.loads(res.data)
      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)

    #Test for playing quiz with questions from a category
    def test_play_quiz_with_category(self):
        quiz = {
            'previous_questions': [6],
            'quiz_category': {'type': 'Entertainment', 'id': '5'}
        }
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #Test for playing quiz with questions from a category that doesn't exist
    def test_play_quiz_with_category_not_found(self):
        quiz = {
            'previous_questions': [6],
            'quiz_category': {'type': 'Bringing', 'id': '9'}
        }
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)


    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()