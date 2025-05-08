from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum
db = SQLAlchemy()

user_categories = db.Table('user_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    categories = db.relationship('Category', secondary=user_categories, backref='users') # Categories as a comma-separated string
    profile_pic = db.Column(db.String(100), default='default.jpg')

    # Relationship to Blog, with back_populates to synchronize with Blog model
    blogs = db.relationship('Blog', back_populates='author', lazy=True)

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Blog model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', back_populates='blogs', lazy=True)

    # Updated relationships
    comments = db.relationship('Comment', back_populates='blog', cascade='all, delete', lazy=True)
    category = db.relationship('Category', backref=db.backref('blogs', lazy=True))

    def __repr__(self):
        return f"<Blog {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'email': self.author.email
            },
            'created_at': self.created_at,
            'category': self.category.name  # Assuming you have a category model
        }

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for comment creation

    # Relationships
    blog = db.relationship('Blog', back_populates='comments', lazy=True)  # Use 'comments' back_populates here
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f"<Comment {self.id} by {self.user.username}>"

# Like model
class Like(db.Model):
    __tablename__ = 'likes'
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    blog = db.relationship('Blog', backref=db.backref('likes', lazy=True))
    user = db.relationship('User', backref=db.backref('likes', lazy=True))

    def __repr__(self):
        return f"<Like {self.user.username} on Blog {self.blog.id}>"

# Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship with Blog
    def __repr__(self):
        return f"{self.name}"


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_category = db.Column(db.String(100))
    improvement = db.Column(db.Text)
    topic_interest = db.Column(db.Text)
    recommend = db.Column(db.Boolean)
    user_experience = db.Column(db.Integer)

    def __repr__(self):
        return f"<Feedback {self.id}>"
    

class TravelEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)
    would_visit_again = db.Column(db.Boolean, default=False)

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(100), nullable=False)
    recipe = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    is_vegetarian = db.Column(db.Boolean, default=False)

class SkinTypeEnum(enum.Enum):
    dry = "Dry"
    oily = "Oily"
    combination = "Combination"

class BeautyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beauty_tips = db.Column(db.Text, nullable=False)
    product_recommendations = db.Column(db.Text, nullable=False)
    skincare_type = db.Column(db.Enum(SkinTypeEnum), nullable=False)

class PoliticsEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    political_issue = db.Column(db.String(100), nullable=False)
    opinion = db.Column(db.Text, nullable=False)
    suggestions = db.Column(db.Text, nullable=False)
    agree_with_policy = db.Column(db.Boolean, default=False)

class HealthyLifestyleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_routine = db.Column(db.Text, nullable=False)
    healthy_meals = db.Column(db.Text, nullable=False)
    wellness_tips = db.Column(db.Text, nullable=False)
    sleeps_early = db.Column(db.Boolean, default=False)