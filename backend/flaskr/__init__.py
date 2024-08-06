import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config) 
  
    with app.app_context():
        db.create_all()
    
    
    #Initialize CORS, Allow '*' for origins 
    CORS(app)


    # This after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # This endpoint will handle all the available categories.
    @app.route("/categories",methods=["GET"])
    def get_categories():
        try:
            category_all = Category.query.all()
            category_list = {category.id: category.type for category in category_all}
            if len(category_list) == 0:
                abort(404)
            return jsonify({"success":True, "categories":category_list})
                
        except KeyError:
            print(sys.exc_info())
            abort(422)
        except Exception as e:
            print(e)
            print(sys.exc_info())
            abort(500)
    
    # An endpoint to handle GET requests for all questions,including pagination (every 10 questions).
    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            page = request.args.get("page",1, type=int)
            questions = Question.query.paginate(page=page, per_page=10)
            questions_list = [question.format() for question in questions.items]
            
            if len(questions_list) == 0:
                abort(404)
            
            categories = Category.query.all()
            categories_dict = {category.id: category.type for category in categories}    
            
            return jsonify({
                "success":True,
                "questions" : questions_list,
                "total_questions": questions.total,
                "categories" : categories_dict,
                "current_category" : None
                })
            
        except KeyError:
            abort(422)
        except Exception as e:
            print(e)
            abort(500)
            

    # An endpoint to handle the DELETE  request for deleting the question using a question ID.
    @app.route("/questions/<int:question_id>",methods=["DELETE"])
    def delete_questions(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        
        if question is None:
            abort(404)
        try:
            question.delete()
            
            return jsonify({
                "success":True,
                "id": question_id
            })
            
        except Exception as e:
            print(f"An error occurred: {e}")
            abort(500)


    #  An endpoint to POST a new question,which will require the question and answer text,category, and difficulty score.
    @app.route("/questions", methods=["POST"])
    def add_questions():
        body = request.get_json()
        
        if not body:
            abort(400, description="Request does not contain a valid JSON body")
        
        if(
            "question" not in body 
            or "answer" not in body
            or "category" not in body
            or "difficulty" not in body
        ):  
            abort(400)
            
        try:
            new_question = body.get("question")
            new_answer = body.get("answer")
            new_category = body.get("category")
            new_difficulty = body.get("difficulty")
            
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            ) 
            
            if any(value == '' for value in [new_question, new_answer, new_category, new_difficulty]):
                print("At least one value is an empty string. ")
                abort(400)
        
            question.insert()
            
            formatted_question = [question.format() for question in Question.query.all()]
            
            return jsonify(
                {
                    "success":True,
                    "created":question.id,
                    "questions":formatted_question,
                    "total_questions":len(formatted_question),
                }
            )
            
        except KeyError:
            abort(422)
        except Exception as e:
            print(e)
            abort(500)


    # This endpoint will return any questions for whom the search termis a substring of the question.
    @app.route("/questions/search", methods=["POST"])
    def search_question_by_term():
        body = request.get_json()
        search_term = body.get("searchTerm")
        search_result = Question.query.filter(
            Question.question.ilike("%{}%".format(search_term))
        ).all()
        
        formatted_question = [question.format() for question in search_result]
        
        if len(formatted_question) == 0 or search_term == "" or search_term == " " :
            abort(404, description="No questions found matching the search term")
            
        if search_term == None  :
            abort(400)
        try:
            return jsonify(
                {
                    "success":True,
                    "questions":formatted_question,
                    "total_questions":len(formatted_question),
                }
            )
            
        except KeyError:
            abort(422)
            
        except Exception as e:
            print(e)
            abort(500)


    # A GET endpoint to get questions based on category.
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_question_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]
        
        if len(formatted_questions) == 0:
            abort(404)
        try:
            return jsonify({
                "success":True,
                "questions":formatted_questions,
                "total_questions":len(formatted_questions),
                "current_category":category_id,
            })
        except Exception as e:
            print(e)
            abort(500)


    # AN endpoint to handle quiz questions
    @app.route("/quizzes", methods=["POST"])
    def get_questions_for_quiz():
        body = request.get_json()
        
        # print("Received body:", body)  # Log the incoming JSON payload
        
        if not body:
            abort(400, description="Request does not contain a valid JSON body")
        
        category_id = body.get("quiz_category",  {})
        quiz_category  = category_id.get('id',None)
        # quiz_category = body.get("quiz_category",  {}).get('id', None)
        previous_questions = body.get("previous_questions",[])
        
        print("Quiz category:", quiz_category)
        print("Previous questions:", previous_questions)
        
        if quiz_category is None or previous_questions is None:
            print("Request missing required fields")
            abort(400, description="Request missing required fields")
        
        if "quiz_category" not in body or "previous_questions"  not in body:
            print("quiz category")
            abort(400)
        
        try:
            if quiz_category == 0:
                random_questions = Question.query.filter(
                    Question.id.not_in(previous_questions)
                ).all()
        
            else:
                random_questions =  Question.query.filter(
                    Question.id.not_in(previous_questions),
                    Question.category == quiz_category,
                ).all()
             
            print("Random questions:", random_questions)
            if not random_questions:
                abort(404, description="No questions available for the specified criteria")
                
            random_question = random.choice(random_questions)
            
            return jsonify({
                "success":True,
                "question": random_question.format()
            })
        except SQLAlchemyError as e:
            print(e)
            abort(500, description="Database error occurred")
        except Exception as e:
            print(e)
            abort(500)
        

#    Error handlers

    @app.errorhandler(400)
    def bad_request(error):
        return ( 
            jsonify({
            "success":False,
            "error": 400,
            "message":"Bad Request",
        }),400,
        )
        
    @app.errorhandler(404)
    def not_found(error):
        return ( 
            jsonify({
            "success":False,
            "error": 404,
            "message":"Not Found",
        }),404,
        )
    
    @app.errorhandler(422)
    def unprocessable_content(error):
        return ( 
            jsonify({
            "success":False,
            "error": 422,
            "message":"Unprocessable Content",
        }),422,
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return ( 
            jsonify({
            "success":False,
            "error": 500,
            "message":"Internal Server Error ",
        }),500,
        )
        
    return app



   