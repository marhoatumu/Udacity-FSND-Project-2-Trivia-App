import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 10

#Pagination function for questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

#Pagination function for categories
def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * CATEGORIES_PER_PAGE
    end = start + CATEGORIES_PER_PAGE

    categories = [category.format() for category in selection]
    current_categories = categories[start:end]

    return current_categories

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    #Get request for all the trivia categories
    @app.route('/categories')
    def get_categories():
        category_selection = Category.query.order_by(Category.id).all()
        formatted_categories = paginate_categories(request, category_selection)

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify({
            'success':True,
            'categories':formatted_categories,
            'total_categories':len(Category.query.all())
            })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    #Endpoint for displaying all available questions page by page
    @app.route('/questions', methods=['GET'])
    def get_questions():
        question_selection = Question.query.order_by(Question.id).all()
        formatted_questions = paginate_questions(request, question_selection)

        if len(formatted_questions) == 0:
            abort(404)
        
        category_selection = Category.query.order_by(Category.id).all()

        return jsonify({
            'success':True,
            'questions':formatted_questions,
            'total_questions':len(Question.query.all()),
            'current_category':'No selected Category',
            'categories':{category.id: category.type for category in category_selection}
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    #Endpoint for deleting a qustion
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            
            question.delete()

            question_selection = Question.query.order_by(Question.id).all()
            formatted_questions = paginate_questions(request, question_selection)

            category_selection = Category.query.order_by(Category.id).all()

            return jsonify({
                'success':True,
                'deleted': question_id,
                'questions':formatted_questions,
                'total_questions':len(Question.query.all()),
                'categories':{category.id: category.type for category in category_selection}
                })
        
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    #Endpoint for adding new questions
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            question.insert()

            question_selection = Question.query.order_by(Question.id).all()
            formatted_questions = paginate_questions(request, question_selection)

            return jsonify({
                'success':True,
                'created': question.id,
                'questions':formatted_questions,
                'total_questions':len(Question.query.all())
                })

        except:
                abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    #Endpoint for searching for questions
    @app.route('/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)

        question_selection = Question.query.filter(Question.question.ilike('%'+search+'%')).all()
        
        if question_selection:
            formatted_questions = paginate_questions(request, question_selection)
            
            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(question_selection),
            })

        else:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    #Endpoint for getting qustions by category
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def question_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            question_selection = Question.query.filter_by(category=str(id)).all()
            formatted_questions = paginate_questions(request, question_selection)

            return jsonify({
                'success':True,
                'questions':formatted_questions,
                'total_questions':len(question_selection),
                'current_category': id
                })
        
        else:
            abort(404)



    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    #Endpoint to play quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')

        try:
            if int(category['id']) == 0:
                question_selection = Question.query.filter(Question.id.not_in_(previousQuestion)).all()
            else:
                question_selection = Question.query.filter(Question.id.not_in_(previousQuestion), Question.category==str(quizCategory['id'])).all()

            current_question = None
            if(question_selection):
                current_question = random.choice(question_selection)

            return jsonify({
                'success':True,
                'question':current_question.format(),
                'current_category': category['type']
                })
        
        except:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    #Error Message Decorators
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Invalid request"
            }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "Method not allowed"
            }), 405

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Request could not be processed"
            }), 422


    return app

