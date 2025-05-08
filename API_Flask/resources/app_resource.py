from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.model import User, Blog, db,Category,TravelEntry,FoodEntry,BeautyEntry,HealthyLifestyleEntry,PoliticsEntry
from flask import session
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import check_password_hash
from flask import request
from werkzeug.utils import secure_filename
import os

jwt = JWTManager() 

class UserRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username is required")
        parser.add_argument('email', required=True, help="Email is required")  # Email field
        parser.add_argument('password', required=True, help="Password is required")
        parser.add_argument('confirm_password', required=True, help="Confirm password is required")  # Confirm password
        parser.add_argument('categories', type=list, location='json', help="Categories list is required")  # Categories field
        data = parser.parse_args()

        # Check if user already exists by username or email
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'User already exists'}, 400

        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400

        # Check if passwords match
        if data['password'] != data['confirm_password']:
            return {'message': 'Passwords do not match'}, 400  # Return an error if passwords don't match

        # Handle categories if they exist, otherwise default to an empty string
        categories = ','.join(data['categories']) if isinstance(data['categories'], list) else ''

        # Create user with email, username, and categories
        user = User(username=data['username'], email=data['email'], categories=categories)  # Join categories into a comma-separated string
        user.set_password(data['password'])  # Set the password hash
        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201


class UserLogin(Resource):
    def post(self):
        # Setting up request parser to get login details
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email is required")  # Changed to 'email'
        parser.add_argument('password', required=True, help="Password is required")
        data = parser.parse_args()

        # Find the user by email
        user = User.query.filter_by(email=data['email']).first()  # Changed to filter by email

        # If the user doesn't exist, return error
        if not user:
            return {'message': 'Invalid email or password'}, 401

        # Check if the provided password matches the stored hash
        if not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid email or password'}, 401

        # If login is successful, create a JWT token for the user
        access_token = create_access_token(identity=user.id)

        # Return the token to the client
        return {'message': 'Login successful', 'access_token': access_token}, 200

class BlogList(Resource):
    @jwt_required()
    def get(self):
        # Return a list of all blogs
        blogs = Blog.query.all()
        return [{'id': b.id, 'title': b.title, 'content': b.content, 'author_id': b.author_id} for b in blogs]

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, help="Title is required")
        parser.add_argument('content', required=True, help="Content is required")
        parser.add_argument('image_filename', required=False, default=None)
        data = parser.parse_args()

        user_id = get_jwt_identity()

        category = Category.query.filter_by(name=data['category']).first()
        if not category:
            category = Category(name=data['category'])
            db.session.add(category)
            db.session.commit()

        blog = Blog(
            title=data['title'],
            content=data['content'],
            category_id=category.id,  # ← correct field
            author_id=user_id,
            image_filename=data['image_filename']
        )


        return {'message': 'Blog created', 'blog_id': blog.id}, 201


class BlogDetail(Resource):
    @jwt_required()
    def get(self, blog_id):
        # Get a specific blog by ID
        blog = Blog.query.get_or_404(blog_id)
        return {'id': blog.id, 'title': blog.title, 'content': blog.content, 'author_id': blog.author_id}

    @jwt_required()
    def put(self, blog_id):
        # Update a blog
        blog = Blog.query.get_or_404(blog_id)
        user_id = get_jwt_identity()

        # Ensure the user is the author
        if blog.author_id != user_id:
            return {'message': 'Not authorized to edit this blog'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('content')
        data = parser.parse_args()

        # Update fields only if they are provided
        if data['title']:
            blog.title = data['title']
        if data['content']:
            blog.content = data['content']

        db.session.commit()
        return {'message': 'Blog updated'}

    @jwt_required()
    def delete(self, blog_id):
        # Delete a blog
        blog = Blog.query.get_or_404(blog_id)
        user_id = get_jwt_identity()

        # Ensure the user is the author
        if blog.author_id != user_id:
            return {'message': 'Not authorized to delete this blog'}, 403

        db.session.delete(blog)
        db.session.commit()
        return {'message': 'Blog deleted'}

UPLOAD_FOLDER = 'static/uploads'

import base64
import uuid
import os
from flask import current_app, request

class CreateBlogAPI(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        print("Incoming data:", data)  # Add this line to inspect incoming data

        title = data.get('title')
        content = data.get('content')
        category_name = data.get('category')  # Category as a string

        # Validate title and content
        if not title or not content:
            return {"message": "Title and content are required"}, 400

        # Check if category exists, create if not
        category = Category.query.filter_by(name=category_name).first()

        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        user_id = get_jwt_identity()

        # Create new blog
        new_blog = Blog(
            title=title,
            content=content,
            category_id=category.id,
            author_id=user_id
        )

        db.session.add(new_blog)
        db.session.commit()

        return {
            "message": "Blog created successfully",
            "blog_id": new_blog.id,
            "image_url": f"/uploads/{data.get('image_filename')}" if data.get('image_filename') else None
        }, 201




# API Resource to Edit a Blog
class EditBlogAPI(Resource):
    @jwt_required()
    def put(self, blog_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, help="Title cannot be blank")
        parser.add_argument('content', required=True, help="Content cannot be blank")
        args = parser.parse_args()

        user_id = get_jwt_identity() 

        # Get the blog to update
        blog = Blog.query.get_or_404(blog_id)

        # Check if the logged-in user is the author of the blog
        if blog.user_id != user_id:
            return {"message": "You are not authorized to edit this blog"}, 403

        # Update the blog
        blog.title = args['title']
        blog.content = args['content']
        db.session.commit()

        return {"message": "Blog updated successfully", "blog_id": blog.id}, 200

# API Resource to Delete a Blog
class DeleteBlogAPI(Resource):
    @jwt_required()
    def delete(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        user_id = get_jwt_identity()

        if blog.author_id != user_id:
            return {'message': 'Not authorized to delete this blog'}, 403

        db.session.delete(blog)
        db.session.commit()

        return {'message': 'Blog deleted successfully'}


model_map = {
    'travel': TravelEntry,
    'food': FoodEntry,
    'beauty': BeautyEntry,
    'politics': PoliticsEntry,
    'healthy_lifestyle': HealthyLifestyleEntry
}

def get_parser(category):
    parser = reqparse.RequestParser()
    
    if category == 'travel':
        parser.add_argument('destination', required=True)
        parser.add_argument('experience', required=True)
        parser.add_argument('recommendations', required=True)
        parser.add_argument('would_visit_again', type=bool, required=False)
    
    elif category == 'food':
        parser.add_argument('dish_name', required=True)
        parser.add_argument('recipe', required=True)
        parser.add_argument('ingredients', required=True)
        parser.add_argument('is_vegetarian', type=bool, required=False)
    
    elif category == 'beauty':
        parser.add_argument('beauty_tips', required=True)
        parser.add_argument('product_recommendations', required=True)
        parser.add_argument('skincare_type', choices=('dry', 'oily', 'combination'), required=True)
    
    elif category == 'politics':
        parser.add_argument('political_issue', required=True)
        parser.add_argument('opinion', required=True)
        parser.add_argument('suggestions', required=True)
        parser.add_argument('agree_with_policy', type=bool, required=False)
    
    elif category == 'healthy_lifestyle':
        parser.add_argument('exercise_routine', required=True)
        parser.add_argument('healthy_meals', required=True)
        parser.add_argument('wellness_tips', required=True)
        parser.add_argument('sleeps_early', type=bool, required=False)

    return parser


class CategoryAPI(Resource):
    def get(self, category):
        Model = model_map.get(category)
        if not Model:
            return {'error': 'Invalid category'}, 400

        entries = Model.query.all()
        results = []
        for entry in entries:
            data = entry.__dict__.copy()
            data.pop('_sa_instance_state', None)
            data['data'] = data.copy()  # For Django compatibility
            results.append(data)
        return results, 200

    def post(self, category):
        Model = model_map.get(category)
        if not Model:
            return {'error': 'Invalid category'}, 400

        parser = get_parser(category)
        args = parser.parse_args()

        # Handle enum conversion for beauty
        if category == 'beauty' and 'skincare_type' in args:
            args['skincare_type'] = args['skincare_type'].lower()

        new_entry = Model(**args)
        db.session.add(new_entry)
        db.session.commit()
        return {'message': 'Entry created successfully'}, 201


class EntryAPI(Resource):
    def put(self, category, entry_id):
        Model = model_map.get(category)
        if not Model:
            return {'error': 'Invalid category'}, 400

        entry = Model.query.get(entry_id)
        if not entry:
            return {'error': 'Entry not found'}, 404

        parser = get_parser(category)
        args = parser.parse_args()

        if category == 'beauty' and 'skincare_type' in args:
            args['skincare_type'] = args['skincare_type'].lower()

        for key, value in args.items():
            setattr(entry, key, value)

        db.session.commit()
        return {'message': 'Entry updated successfully'}, 200

    def delete(self, category, entry_id):
        Model = model_map.get(category)
        if not Model:
            return {'error': 'Invalid category'}, 400

        entry = Model.query.get(entry_id)
        if not entry:
            return {'error': 'Entry not found'}, 404

        db.session.delete(entry)
        db.session.commit()
        return {'message': 'Entry deleted successfully'}, 200
