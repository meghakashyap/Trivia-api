import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        config = dotenv_values()
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
                config["DATABASE_USERNAME"],
                config["DATABASE_PASSWORD"],
                config["DATABASE_HOST"]+ ":" + config["PORT"],
                self.database_name)
    
        
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })
        
        self.client = self.app.test_client()


        # binds the app to the current context
        with self.app.app_context():
        
            db.create_all()
            
        self.new_question = {
            "question": "who invented computer",
            "answer": "Charles",
            "category": 1,
            "difficulty": 1,
        }
        self.new_question_invalid_body = {
            "question": "who invented computer",
            "answer": "Charles",
            "category": 1,
        }
        self.new_quiz =  {
            "quiz_category": {"id": 1, "type": "science"},
            "previous_questions": [5,12]
        }
        self.new_quiz_invalid = {"quiz_category": 44, "previous_questions": [999]}

       
    
    def tearDown(self):
        """Executed after reach test"""
        pass
        

    # Test cases for listing all categories
    def test_all_categories(self):
        res = self.client.get("/categories")
        data = res.get_json()
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data))

    def test_404_all_categories(self):
        res = self.client.get("/categories/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    # Test cases for listing all questions
    def test_get_questions(self):
        res = self.client.get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_404_get_questions(self):
        res = self.client.get("/questionss")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    # Test cases for add question endpoint
    def test_add_question(self):
        res = self.client.post("/questions", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        return data["questions"][-1]["id"]

    def test_400_get_questions(self):
        res = self.client.post("/questions", json=self.new_question_invalid_body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # Test cases for delete endpoint
    def test_delete_question(self):
        question_id = self.test_add_question()
        delete_path = "/questions/" + str(question_id)
        res = self.client.delete(delete_path)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_invalid(self):
        res = self.client.delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    # Test cases for search endpoint
    def test_search_question(self):
        res = self.client.post("/questions/search", json={"searchTerm": "Tom"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_404_search_no_question(self):
        res = self.client.post("/questions/search", json={"searchTerm": "test111"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    # Test cases for GET endpoint to get questions based on category
    def test_get_ques_from_category(self):
        res = self.client.get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_404_get_ques_from_invalid_category(self):
        res = self.client.get("/categories/10/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    # Test cases for quizz endpoint
    def test_quizz(self):
        res = self.client.post("/quizzes", json=self.new_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["question"]))

    def test_422_invalid_quizz(self):
        res = self.client.post("/quizzes", json=self.new_question_invalid_body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()