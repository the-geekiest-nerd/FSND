# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API Reference

## Getting Started
Base URL: At present, this app can only be run locally. The backend app is hosted at the default `http://localhost:5000`, which is set as a proxy
in the frontend configuration.

Authentication: This version of the application does not require any kind of authentication.

## Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "error": 404,
    "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
    "success": false
}
```

The API will return the following errors based on how the request fails:
 - 400: Bad Request
 - 404: Not Found
 - 405: Method Not Allowed
 - 422: Unprocessable Entity
 - 500: Internal Server Error

## Endpoints

#### GET /
 - General
   - root endpoint
   - can also work to check if the api is up and running
 
 - Sample Request
   - `http://localhost:5000`

<details>
<summary>Sample Response</summary>

```
{
    "health": "Running!!"
}
```

</details>

#### GET /categories
 - General
   - get all the available categories
 
 - Sample Request
   - `http://localhost:5000/categories`

<details>
<summary>Sample Response</summary>

```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    }
}
```

</details>

#### GET /questions
 - General
   - get questions list
   - questions are paginated in groups of <b>10</b> (can not be configured from the front end)
 
 - Query Parameters
   - page: Optional
   - search_term: Optional
   - current_category: Optional
 
 - Sample Requests
   - `http://localhost:5000/questions`
   - `http://localhost:5000/questions?page=2`
   - `http://localhost:5000/questions?search_term=w`

<details>
<summary>Sample Response for http://localhost:5000/questions</summary>

```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": null,
    "questions": [
        {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 11,
            "question": "Which country won the first ever soccer World Cup in 1930?"
        },
        {
            "answer": "George Washington Carver",
            "category": 4,
            "difficulty": 2,
            "id": 12,
            "question": "Who invented Peanut Butter?"
        },
        {
            "answer": "Lake Victoria",
            "category": 3,
            "difficulty": 2,
            "id": 13,
            "question": "What is the largest lake in Africa?"
        },
        {
            "answer": "The Palace of Versailles",
            "category": 3,
            "difficulty": 3,
            "id": 14,
            "question": "In which royal palace would you find the Hall of Mirrors?"
        },
        {
            "answer": "Agra",
            "category": 3,
            "difficulty": 2,
            "id": 15,
            "question": "The Taj Mahal is located in which Indian city?"
        },
        {
            "answer": "Escher",
            "category": 2,
            "difficulty": 1,
            "id": 16,
            "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
        },
        {
            "answer": "Mona Lisa",
            "category": 2,
            "difficulty": 3,
            "id": 17,
            "question": "La Giaconda is better known as what?"
        },
        {
            "answer": "One",
            "category": 2,
            "difficulty": 4,
            "id": 18,
            "question": "How many paintings did Van Gogh sell in his lifetime?"
        },
        {
            "answer": "Jackson Pollock",
            "category": 2,
            "difficulty": 2,
            "id": 19,
            "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        },
        {
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4,
            "id": 20,
            "question": "What is the heaviest organ in the human body?"
        }
    ],
    "search_term": "",
    "total_questions": 16
}
```
  
</details>

#### DELETE /questions/{question_id}
 - General
   - delete a question using question_id
 
 - Sample Request
   - `http://localhost:5000/questions/1`

<details>
<summary>Sample Response</summary>

```
{
    "success": true
}
```
  
</details>

#### POST /questions
 - General
   - create a question
 
 - Request Body
   - question: string, required
   - answer: string, required
   - category: string | number, required
   - difficulty: number, required
 
 - Sample Request
   - `http://localhost:5000/questions`
   - Request Body
     ```
       {
            "question": "Which is the test framework used in this project?",
            "answer": "unittest",
            "category": "1",
            "difficulty": 1
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "success": true
}
```
  
</details>

#### POST /questions/search
 - General
   - search the questions list based on a search term or category
 
 - Request Body
   - searchTerm: string, required
   - currentCategory: string, required
 
 - Sample Request
   - `http://localhost:5000/questions/search`
   - Request Body
     ```
       {
            "searchTerm": "who",
            "currentCategory": "1"
        }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": "1",
    "questions": [
        {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 21,
            "question": "Who discovered penicillin?"
        }
    ],
    "search_term": "who",
    "total_questions": 1
}
```
  
</details>

#### GET /categories/<category_id>/questions
 - General
   - get questions for a particular category
 
 - Sample Request
   - `http://localhost:5000/categories/2/questions`

<details>
<summary>Sample Response</summary>

```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": "2",
    "questions": [
        {
            "answer": "Escher",
            "category": 2,
            "difficulty": 1,
            "id": 16,
            "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
        },
        {
            "answer": "Mona Lisa",
            "category": 2,
            "difficulty": 3,
            "id": 17,
            "question": "La Giaconda is better known as what?"
        },
        {
            "answer": "One",
            "category": 2,
            "difficulty": 4,
            "id": 18,
            "question": "How many paintings did Van Gogh sell in his lifetime?"
        },
        {
            "answer": "Jackson Pollock",
            "category": 2,
            "difficulty": 2,
            "id": 19,
            "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        }
    ],
    "search_term": "",
    "total_questions": 4
}
```

</details>

#### POST /quizzes
 - General
   - get random questions from the selected category to play the quiz
 
 - Request Body
   - previous_questions: array, required (contains a list of questions that have already been played)
   - quiz_category: object
     - id: string | number, required
 
 - Sample Request
   - `http://localhost:5000/quizzes`
   - Request Body
     ```
     {
        "previous_questions": [16, 17],
        "quiz_category": {
            "id": "2"
        }
     }
     ```
   
<details>
<summary>Sample Response</summary>

```
{
    "question": {
        "answer": "One",
        "category": 2,
        "difficulty": 4,
        "id": 18,
        "question": "How many paintings did Van Gogh sell in his lifetime?"
    }
}
```
  
</details>

## Testing
For testing the backend, run the following commands (in the exact order):
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py