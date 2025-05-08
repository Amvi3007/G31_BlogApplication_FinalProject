from flask import Flask, render_template, redirect, request, url_for, flash,session
import os
from models.model import db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from models.model import User, Blog ,Comment,Like,Category,Feedback
from flask_restful import Api
from resources.app_resource import jwt
from resources.app_resource import UserLogin
from resources.app_resource import UserRegister
from resources.app_resource import BlogList
from resources.app_resource import BlogDetail,CreateBlogAPI,EditBlogAPI,DeleteBlogAPI
from datetime import datetime 
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from resources.app_resource import CategoryAPI, EntryAPI

basedir = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
jwt.init_app(app)
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Ensure the image is saved here
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Set a secure key for JWT
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Add your allowed extensions
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Ensure the uploads folder exists when the app starts
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False



db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()

    # Check if an admin user already exists
    if not User.query.filter_by(role="admin").first():
        admin_user = User(username="admin", email="admin@gmail.com", role="admin")  # Add username here
        admin_user.set_password("admin123")  # Set a default password
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with email: admin@gmail.com and password: admin123")


# Regular Routes (For rendering templates)
@app.route('/')
def dashboard():
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    search_query = request.args.get('search', '').strip()
    category_name = request.args.get('category', '').strip()

    blogs_query = Blog.query

    # Search filter
    if search_query:
        blogs_query = blogs_query.filter(
            (Blog.title.ilike(f'%{search_query}%')) |
            (Blog.content.ilike(f'%{search_query}%'))
        )

    # Category filter
    if category_name:
        blogs_query = blogs_query.join(Category).filter(Category.name == category_name)

    # Fetch filtered blogs
    blogs = blogs_query.order_by(Blog.created_at.desc()).all()

    # Manually define categories
    categories = ['Food', 'Travel', 'Beauty & Makeup', 'Healthy Lifestyle', 'Politics']

    # Render the template with blogs and predefined categories
    return render_template(
        'home1.html',
        blogs=blogs,
        categories=categories,
        search_query=search_query,
        selected_category=category_name
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Query the database for the user
        user = User.query.filter_by(email=email).first()

        # Validate user and password
        if user and user.check_password(password):
            login_user(user)  # Use login_user from Flask-Login to set current_user
            session["email"] = email  # Optionally store email in session, though Flask-Login does this too
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("login.html")

    return render_template("login.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        categories = request.form.getlist("category")

        # Ensure all fields are populated
        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("signup"))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("signup"))

        # Create new user with role 'user' by default
        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)

        # Handle categories (optional, depending on whether you store them in the User model as a list or string)
        if categories:
            selected_categories = Category.query.filter(Category.name.in_(categories)).all()
            new_user.categories = selected_categories  # ✅ Assign list of Category objects


        # Add the new user to the session and commit
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    # Categories could come from a database or be hardcoded
    categories = ["Food", "Beauty", "Politics", "Travel", "Lifestyle"]
    return render_template("signup.html", categories=categories)



# Route for about page
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                current_user.profile_pic = filename
                db.session.commit()
            else:
                flash('Invalid file format!', 'danger')

    # Pass current_user.categories to the template
    return render_template('profile.html', user=current_user)


# Admin required wrapper
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Access denied!", "danger")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/admin')
@login_required
@admin_required
def admin():
    return "Welcome to the admin panel!"

@login_required
@app.route("/my_blogs")
def my_blogs():
    if not current_user.is_authenticated:
        flash("You need to login first", "warning")
        return redirect(url_for("login"))

    user_id = current_user.id
    blogs = Blog.query.filter_by(author_id=user_id).all()

    # Add image URL for each blog
    for blog in blogs:
        if blog.image_filename:
            blog.image_url = url_for('static', filename='uploads/' + blog.image_filename)
        else:
            blog.image_url = url_for('static', filename='default.jpg')  # Provide default image if none exists

    if not blogs:
        flash("You have not written any blogs yet.", "info")

    return render_template("myblogs.html", blogs=blogs)


import os
from werkzeug.utils import secure_filename


@app.route('/create_blog', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in before allowing access
def create_blog():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_name = request.form['category']  # Get selected category from dropdown

        # Handle image upload
        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Query the category by name
        # Assuming 'category_name' is the value passed from the form
        category_name = request.form['category']  # Get selected category from dropdown

        # Query the category by name
        category = Category.query.filter_by(name=category_name).first()

        if category is None:
            # Handle case if category is not found (this shouldn't happen with your dropdown options)
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        # Create and save the blog
        new_blog = Blog(
            title=title,
            content=content,
            image_filename=image_filename,
            author=current_user,
            author_id=current_user.id,
            category=category  # Store the category object
        )
        db.session.add(new_blog)
        db.session.commit()


        return redirect(url_for('view_blog', blog_id=new_blog.id))

    return render_template('create_blog.html')

@login_required
@app.route('/edit_blog/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)  # Get the blog by ID
    categories = Category.query.all()  # Get all categories from the Category table
    
    if request.method == 'POST':
        # Update blog fields with form data
        blog.title = request.form['title']
        blog.content = request.form['content']

        # Image handling: if a new image is uploaded, save it
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static/uploads', filename)  # Path to save the image
                image_file.save(image_path)  # Save the file to the path
                blog.image_filename = filename  # Update blog's image filename
        
        db.session.commit()  # Save the changes to the database
        return redirect(url_for('view_blog', blog_id=blog.id))  # Redirect to the blog view page

    return render_template('edit_blog.html', blog=blog, categories=categories)

# Delete Blog View
@app.route("/delete_blog/<int:blog_id>", methods=["POST"])
@login_required
def delete_blog(blog_id):
    # Get the blog to delete
    blog = Blog.query.get_or_404(blog_id)
    
    # Check if the logged-in user is the author of the blog
    if blog.author_id != current_user.id:
        flash("You are not authorized to delete this blog.", "danger")
        return redirect(url_for("home"))
    
    # Manually delete related like records first
    likes = Like.query.filter_by(blog_id=blog.id).all()
    for like in likes:
        db.session.delete(like)
    
    # Manually delete related comments
    comments = Comment.query.filter_by(blog_id=blog.id).all()
    for comment in comments:
        db.session.delete(comment)
    
    # Now delete the blog
    db.session.delete(blog)
    db.session.commit()
    
    return redirect(url_for("home"))



@app.route('/view_blog/<int:blog_id>')
def view_blog(blog_id):
    # Retrieve the blog by its ID or return 404 if not found
    blog = Blog.query.get_or_404(blog_id)

    # Get the image URL (check if image exists)
    image_url = None
    if blog.image_filename:
        # Ensure the image exists in the static/uploads folder
        image_url = url_for('static', filename='uploads/' + blog.image_filename)

    # Count the number of likes (ensure blog.likes is a relationship/list)
    like_count = len(blog.likes) if hasattr(blog, 'likes') else 0

    # Retrieve the author's categories (assuming 'categories' is a string field in User model)
    # If there are categories available, use them; otherwise, default to "Uncategorized"
    category = blog.author.categories if (blog.author and blog.author.categories) else "Uncategorized"

    # Pass everything to the template
    return render_template(
        'view_blog.html',
        blog=blog,
        like_count=like_count,
        category=category,
        image_url=image_url
    )




@app.route('/add_comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    if request.method == 'POST':
        content = request.form['content']
        blog = Blog.query.get(blog_id)
        user = current_user  # Assuming you're using Flask-Login
        new_comment = Comment(content=content, blog_id=blog.id, user_id=user.id)
        
        db.session.add(new_comment)
        db.session.commit()
        
        return redirect(url_for('view_blog', blog_id=blog.id))


from flask import jsonify, request

@app.route('/like/<int:blog_id>', methods=['POST'])
@login_required
def like_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    # Check if the user has already liked this blog
    existing_like = Like.query.filter_by(blog_id=blog_id, user_id=current_user.id).first()

    if existing_like:
        return jsonify({'error': 'You have already liked this blog!'}), 400

    # If not, create a new like
    like = Like(blog_id=blog.id, user_id=current_user.id)
    db.session.add(like)
    db.session.commit()

    # Return the updated like count
    like_count = Like.query.filter_by(blog_id=blog_id).count()
    return jsonify({'message': 'You liked this blog!', 'like_count': like_count}), 200

@app.route('/api/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
    image = request.files.get('image')
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'filename': filename}), 200
    return jsonify({'message': 'No image provided'}), 400

@app.route('/api/save-user-profile-pic', methods=['POST'])
def save_user_profile_pic():
    data = request.get_json()
    user_id = data.get('user_id')
    profile_pic_filename = data.get('profile_pic')

    # Store in your Flask DB
    # Save or update user profile with the image filename
    user = User.query.get(user_id)
    if user:
        user.profile_pic = profile_pic_filename
        db.session.commit()

    return jsonify({'message': 'User profile picture saved'}), 200

@app.route('/api/save-blog-image', methods=['POST'])
def save_blog_image():
    data = request.get_json()
    blog_id = data.get('blog_id')
    image_filename = data.get('image_filename')
    author_id = data.get('author_id')

    # Store in your Flask DB
    # Save blog image filename with the blog
    blog = Blog.query.get(blog_id)
    if blog:
        blog.image_filename = image_filename
        db.session.commit()

    return jsonify({'message': 'Blog image saved'}), 200


from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/create_blog', methods=['POST'])
@jwt_required()
def create_new_blog():
    try:
        # Get user ID from the JWT token
        user_id = get_jwt_identity()
        user_id = int(user_id)
        user = User.query.get(user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        # Get data from the request
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        category_name = data.get('category')
        image_filename = data.get('image_filename')

        # Log the incoming data for debugging
        app.logger.info(f"Received Data: {data}")

        # Validate data
        if not all([title, content, category_name]):
            return jsonify({"msg": "Title, content, and category are required"}), 400

        # Find or create category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        # Create the new blog
        new_blog = Blog(
            title=title,
            content=content,
            category_id=category.id,
            author_id=user.id,
            image_filename=image_filename
        )

        # Add blog to the database
        db.session.add(new_blog)
        db.session.commit()

        return jsonify({"msg": "Blog created successfully"}), 201

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")  # Log the exception
        db.session.rollback()
        return jsonify({"msg": f"Unexpected error occurred: {str(e)}"}), 500


@app.route('/add_categories', methods=['POST'])
def add_categories_endpoint():
    # Predefined list of categories
    categories = ['Food', 'Travel', 'Beauty', 'Healthy Lifestyle', 'Politics']
    
    for category_name in categories:
        # Check if category exists
        existing_category = Category.query.filter_by(name=category_name).first()
        if not existing_category:
            # Add category to database
            new_category = Category(name=category_name)
            db.session.add(new_category)

    db.session.commit()
    return jsonify({"msg": "Categories added successfully!"}), 200

from werkzeug.security import check_password_hash


@app.route('/loginapi', methods=['POST'])
def login_api():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if user:
        # Validate password using check_password_hash
        if check_password_hash(user.password, password):  # Use check_password_hash here
            # Generate a JWT token and return it
            access_token = create_access_token(identity=str(user.id))  # Convert user.id to string
            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"msg": "Invalid password"}), 401
    else:
        return jsonify({"msg": "Invalid username or password"}), 401


@app.route('/registerapi', methods=['POST'])
def register_api():
    data = request.get_json()

    # Extract user data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    categories = data.get('categories', [])

    # Validate that the passwords match
    if password != confirm_password:
        return jsonify({"msg": "Passwords do not match!"}), 400

    # Check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists!"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method='scrypt')

    # Create a new user object
    new_user = User(username=username, email=email, password=hashed_password)

    # Get the categories and add them to the user
    selected_categories = []
    for category_name in categories:
        category = Category.query.filter_by(name=category_name).first()
        if category:
            selected_categories.append(category)
        else:
            # If category doesn't exist, create a new category
            new_category = Category(name=category_name)
            db.session.add(new_category)
            selected_categories.append(new_category)

    new_user.categories = selected_categories

    # Save to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully!", "user_id": new_user.id}), 201

@app.route('/api/blogs', methods=['GET'])
def get_all_blogs():
    blogs = Blog.query.all()

    blog_list = []
    for blog in blogs:
        blog_data = {
            "id": blog.id,
            "title": blog.title,
            "content": blog.content,
            "category": blog.category.name,   # accessing related Category
            "author": blog.author.username,  # accessing related User
            "image_filename": blog.image_filename,
            "like_count": blog.like_count,
            "created_at": blog.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        blog_list.append(blog_data)

    return jsonify(blog_list), 200


@app.route('/logoutapi', methods=['GET'])
def logout_api():
    logout_user()  # Log the user out
    return jsonify({"msg": "Logged out successfully"}), 200


@app.route('/api/edit_blog/<int:blog_id>', methods=['PUT'])
def update_blog(blog_id):
    data = request.get_json()

    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({"msg": "Blog not found"}), 404

    # Optional updates
    if 'title' in data:
        blog.title = data['title']
    if 'content' in data:
        blog.content = data['content']
    if 'category' in data:
        category = Category.query.filter_by(name=data['category']).first()
        if not category:
            return jsonify({"msg": f"Category '{data['category']}' does not exist"}), 400
        blog.category_id = category.id
    if 'image_filename' in data:
        blog.image_filename = data['image_filename']

    db.session.commit()

    return jsonify({"msg": "Blog updated successfully"}), 200

@app.route('/blogs/<int:blog_id>', methods=['GET'])
def get_blog(blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({"msg": "Blog not found"}), 404

    blog_data = {
        "id": blog.id,
        "title": blog.title,
        "content": blog.content,
        "category": blog.category.name,
        "author": blog.author.username,
        "image_filename": blog.image_filename,
        "like_count": blog.like_count,
        "created_at": blog.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(blog_data), 200

@app.route('/api/delete_blog/<int:blog_id>', methods=['DELETE'])
def delete_new_blog(blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({"msg": "Blog not found"}), 404

    db.session.delete(blog)
    db.session.commit()

    return jsonify({"msg": f"Blog with ID {blog_id} deleted successfully."}), 200

@app.route('/api/blog/<int:blog_id>/like', methods=['POST'])
@jwt_required()
def like_new_blog(blog_id):
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    blog = Blog.query.get_or_404(blog_id)

    # Check if user already liked
    existing_like = Like.query.filter_by(user_id=user_id, blog_id=blog_id).first()
    if existing_like:
        return jsonify({"msg": "Already liked"}), 400

    like = Like(user_id=user_id, blog_id=blog_id)
    db.session.add(like)

    # Increment like count in Blog model
    blog.like_count += 1
    db.session.commit()

    return jsonify({"msg": "Blog liked"}), 200

@app.route('/api/blog/<int:blog_id>/unlike', methods=['POST'])
def unlike_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    like = Like.query.filter_by(user_id=current_user.id, blog_id=blog_id).first()
    if not like:
        return jsonify({"msg": "Not liked yet"}), 400

    db.session.delete(like)

    # Decrement like count
    blog.like_count = max(blog.like_count - 1, 0)
    db.session.commit()

    return jsonify({"msg": "Blog unliked"}), 200

@app.route('/api/blog/<int:blog_id>/comment', methods=['POST'])
@jwt_required()  # Use jwt_required without arguments
def comment_new_blog(blog_id):
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"msg": "Comment content is required"}), 400

    # Get the user identity from the JWT token
    user_id = get_jwt_identity()

    # You don't need current_user, because you're using JWT now
    blog = Blog.query.get_or_404(blog_id)

    comment = Comment(content=content, blog_id=blog_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"msg": "Comment added"}), 201

@app.route('/api/blog/<int:blog_id>/comments', methods=['GET'])
def get_comments(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    comments = Comment.query.filter_by(blog_id=blog_id).all()

    comment_list = []
    for comment in comments:
        comment_list.append({
            "id": comment.id,
            "content": comment.content,
            "user": comment.user.username,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({"comments": comment_list})

@app.route('/api/blog/<int:blog_id>/likes', methods=['GET'])
def get_likes(blog_id):
    likes = Like.query.filter_by(blog_id=blog_id).all()
    user_list = [like.user.username for like in likes]
    return jsonify({"likes": user_list, "like_count": len(user_list)})


@app.route('/submit', methods=['POST'])
def submit_feedback():
    feedback_category = request.form.get('feedback_category')
    improvement = request.form.get('improvement')
    topic_interest = request.form.get('topic_interest')
    recommend = True if request.form.get('recommend') == 'yes' else False
    user_experience = request.form.get('user_experience')

    feedback = Feedback(
        feedback_category=feedback_category,
        improvement=improvement,
        topic_interest=topic_interest,
        recommend=recommend,
        user_experience=int(user_experience)
    )

    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for('thankyou'))

CATEGORY_CHOICES = [
    ('bug', 'Bug Report'),
    ('feature', 'Feature Request'),
    ('general', 'General Feedback'),
    ('ui/ux feedback','UI/UX Feedback'),
    ('other','Other')
]

INTEREST_CHOICES = [
   ('travel', 'Travel'),
    ('politics', 'Politics'),
    ('healthy_lifestyle', 'Healthy Lifestyle'),
    ('beauty', 'Beauty'),
    ('food', 'Food'),
]

@app.route('/getfeedback', methods=['GET', 'POST'])
def submit_new_feedback():
    if request.method == 'POST':
        # Retrieving form data
        feedback_category = request.form.get('feedback_category')
        improvement = request.form.get('improvement')
        topic_interest = request.form.getlist('topic_interest')  # Checkboxes return a list
        recommend = request.form.get('recommend')
        user_experience = request.form.get('user_experience')

        # Convert "recommend" to boolean
        recommend = True if recommend == 'yes' else False

        # Create and store feedback in the database
        feedback = Feedback(
            feedback_category=feedback_category,
            improvement=improvement,
            topic_interest=",".join(topic_interest),  # Join list of topics
            recommend=recommend,
            user_experience=int(user_experience)
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(url_for('thankyou'))

    return render_template('feedback_form.html', category_choices=CATEGORY_CHOICES, interest_choices=INTEREST_CHOICES)


@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# Flask-RESTful API Routes
api.add_resource(UserRegister, "/registerapi")
api.add_resource(UserLogin, "/loginapi")
api.add_resource(BlogList, "/api/blogs")
api.add_resource(BlogDetail, "/blogs/<int:blog_id>")
api.add_resource(CreateBlogAPI, '/api/create_blog')
api.add_resource(EditBlogAPI, '/api/edit_blog/<int:blog_id>')
api.add_resource(DeleteBlogAPI, '/api/delete_blog/<int:blog_id>')
api.add_resource(CategoryAPI, '/api/forum/<string:category>')
api.add_resource(EntryAPI, '/api/forum/<string:category>/<int:entry_id>')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)