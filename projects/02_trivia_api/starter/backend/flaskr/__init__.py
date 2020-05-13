import os
import sys

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/')
    def health():
        return jsonify({'health': 'Running!!'})

    @app.route('/categories')
    def get_categories():
        categories_query = Category.query.order_by(Category.id).all()
        categories_data = {}

        if len(categories_query) == 0:
            abort(500)

        for category in categories_query:
            categories_data[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_data
        })

    @app.route('/questions')
    def get_questions():
        search_term = request.args.get('search_term', '')
        current_category = request.args.get('current_category', None)
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        try:
            questions_query = Question.query.filter(Question.question.ilike("%{}%".format(search_term)))

            if current_category != '':
                questions_query = questions_query.filter(Question.category == current_category)

            questions_query = questions_query.order_by(Question.id).all()
            questions_data = [question.format() for question in questions_query]

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': questions_data[start:end],
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': current_category,
                'search_term': search_term
            })

        except:
            abort(500)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        question = Question.query.get_or_404(question_id)

        try:
            question.delete()
            return jsonify({
                'success': True
            })

        except:
            print(sys.exc_info(), file=sys.stderr)
            abort(500)

    @app.route('/questions', methods=['POST'])
    def create_question():

        try:
            request_body = request.get_json()
            if request_body['question'] == '' or request_body['answer'] == '':
                abort(422)

            new_question = Question(
                request_body['question'],
                request_body['answer'],
                request_body['difficulty'],
                request_body['category']
            )

            new_question.insert()

            return jsonify({
                'success': True
            })

        except:
            abort(500)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            questions_search_term = request.get_json()['searchTerm']
            current_category = request.get_json()['currentCategory']
            questions_query = Question.query.filter(
                Question.category == current_category,
                Question.question.ilike("%{}%".format(questions_search_term))
            ).order_by(Question.id).all()
            questions_data = [question.format() for question in questions_query]

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': questions_data[:QUESTIONS_PER_PAGE],
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': current_category,
                'search_term': questions_search_term
            })

        except:
            abort(500)

    @app.route('/categories/<category_id>/questions')
    def get_category_specific_question(category_id):
        try:
            questions_search_term = request.args.get('search_term', '')
            questions_query = Question.query.filter(
                Question.category == category_id,
                Question.question.ilike("%{}%".format(questions_search_term))
            ).order_by(Question.id).all()
            questions_data = [question.format() for question in questions_query]

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': questions_data[:QUESTIONS_PER_PAGE],
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': category_id,
                'search_term': questions_search_term
            })

        except:
            abort(500)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.errorhandler(404)
    @app.errorhandler(422)
    @app.errorhandler(500)
    def error_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    return app
