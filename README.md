README.txt
==========

Description:
------------
This project demonstrates a hybrid web application architecture where Flask serves as the RESTful API provider, and Django acts as the API consumer and front-end renderer. The system enables two main features:

1. Interactive Conference 
2. Feedback Collection 

Project Structure:
------------------
1. **Flask App (API Provider)**  
   - Hosts RESTful APIs 
   - Built using Flask and Flask-RESTful
   - Acts as a microservice that communicates via JSON 

2. **Django App (API Consumer + Frontend)**  
   - Fetches conference data and feedback from Flask API using requests
   - Renders views and templates 
   - Uses Django ORM for user management and local data handling

Usage Instructions:
-------------------
1. **Setup Flask API Server:**
   - Navigate to the Flask project directory
   - Create a virtual environment and install dependencies
     ```
     pip install -r requirements.txt
     ```
   - Run the Flask server
     ```
     python app.py
     ```
   - Flask will serve the API at `http://localhost:5000/`

2. **Setup Django Frontend Project:**
   - Navigate to the Django project directory
   - Create a virtual environment and install dependencies
     ```
     pip install -r requirements.txt
     ```
   - Run migrations and create a superuser
     ```
     python manage.py migrate
     python manage.py createsuperuser
     ```
   - Run the Django development server
     ```
     python manage.py runserver
     ```
   - Access the frontend at `http://localhost:8000/`

3. **Communication Flow:**
   - Django uses Python's `requests` module to call Flask API endpoints
   - Data fetched from Flask is processed and rendered by Django views
   - Feedback submitted through Django is forwarded to Flask for storage/processing


Key Django Functionalities:
---------------------------
- Conference Page: An interactive conference system with a Django frontend and Flask RESTful backend that enables category-based CRUD operations.
- Feedback Form: Allows users to submit feedback which is sent to Flask API
- Admin Panel: Managed through Django’s default admin interface

Dependencies:
-------------
- Flask
- Flask-RESTful
- Django
- requests
- Python 3.8+

Author:
-------
Amvi (CSE with AI, Chitkara University)


