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
        return jsonify({'health': 'Running!!'}), 200

    @app.route('/categories')
    def get_categories():
        categories_query = Category.query.order_by(Category.id).all()
        categories_data = {}

        if len(categories_query) == 0:
            abort(500)

        for category in categories_query:
            categories_data[category.id] = category.type

        return jsonify({
            'categories': categories_data
        }), 200

    @app.route('/questions')
    def get_questions():
        search_term = request.args.get('search_term', '')
        current_category = request.args.get('current_category', None)
        current_category = None if current_category == '' else current_category
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        try:
            questions_query = Question.query.filter(Question.question.ilike("%{}%".format(search_term)))

            if current_category is not None:
                questions_query = questions_query.filter(Question.category == current_category)

            questions_query = questions_query.order_by(Question.id).all()
            questions_data = [question.format() for question in questions_query]
            selected_questions_data = questions_data[start:end]

            if len(selected_questions_data) == 0:
                raise IndexError

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'questions': selected_questions_data,
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': current_category,
                'search_term': search_term
            }), 200

        except IndexError:
            abort(404)

        except:
            abort(500)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        question = Question.query.get_or_404(question_id)

        try:
            question.delete()
            return jsonify({
                'success': True
            }), 200

        except:
            abort(500)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            request_body = request.get_json()
            if request_body['question'] == '' or request_body['answer'] == '':
                raise TypeError

            new_question = Question(
                request_body['question'],
                request_body['answer'],
                request_body['category'],
                request_body['difficulty']
            )

            new_question.insert()

            return jsonify({
                'success': True
            }), 201

        except TypeError:
            abort(422)

        except:
            abort(500)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            request_body = request.get_json()

            if 'searchTerm' not in request_body or 'currentCategory' not in request_body:
                raise TypeError

            questions_search_term = request_body['searchTerm']
            current_category = request_body['currentCategory']
            questions_query = Question.query.filter(Question.question.ilike("%{}%".format(questions_search_term)))

            if current_category is not None:
                questions_query = questions_query.filter(Question.category == current_category)

            questions_query = questions_query.order_by(Question.id).all()
            questions_data = [question.format() for question in questions_query]

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'questions': questions_data[:QUESTIONS_PER_PAGE],
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': current_category,
                'search_term': questions_search_term
            }), 200

        except TypeError:
            abort(400)

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

            if len(questions_data) == 0:
                raise IndexError

            categories_query = Category.query.order_by(Category.id).all()
            categories_data = {}

            for category in categories_query:
                categories_data[category.id] = category.type

            return jsonify({
                'questions': questions_data[:QUESTIONS_PER_PAGE],
                'total_questions': len(questions_data),
                'categories': categories_data,
                'current_category': category_id,
                'search_term': questions_search_term
            }), 200

        except IndexError:
            abort(404)

        except:
            abort(500)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            request_body = request.get_json()

            if 'previous_questions' not in request_body \
                    or 'quiz_category' not in request_body \
                    or 'id' not in request_body['quiz_category']:
                raise TypeError

            previous_questions = request_body['previous_questions']
            category_id = request_body['quiz_category']['id']
            questions_query = Question.query.with_entities(Question.id).filter(Question.id.notin_(previous_questions))

            if category_id != 0:
                questions_query = questions_query.filter(Question.category == str(category_id))

            questions_query = questions_query.order_by(Question.id).all()
            question_ids = [q.id for q in questions_query]

            if len(question_ids) == 0:
                return jsonify({
                    'question': None
                }), 200

            random_question_id = random.choice(question_ids)
            next_question = Question.query.get(random_question_id).format()

            return jsonify({
                'question': next_question
            }), 200

        except TypeError:
            abort(400)

        except:
            abort(500)

    @app.errorhandler(400)
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
