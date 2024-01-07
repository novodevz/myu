# app.py

import datetime

# import jwt
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from image_handler import handle_uploaded_file

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myU.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ROOT_URL"] = "localhost:5000/"
app.config["UPLOAD_FOLDER"] = "static/images/uploads"
app.config["DEFAULT_IMG"] = "static/images/uploads/default.jpg"

# Configure JWT settings
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this to a secure secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(
    hours=1
)  # Set the expiration time
app.config["JWT_ALGORITHM"] = "HS256"  # Set the algorithm

# Initialize JWT extension
jwt = JWTManager(app)

app.secret_key = "devkey"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    img = db.Column(db.String(255), nullable=False)

    # Define one-to-many relationship with Grade
    grades = db.relationship("Grade", backref="user", lazy=True)

    def __init__(self, email, hashed_pw, img):
        self.email = email
        self.hashed_pw = hashed_pw
        self.img = img

        # Set the username based on the email if not provided
        self.username = self.email.split("@")[0]


# Course class
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    # Define one-to-many relationship with Grade
    grades = db.relationship("Grade", backref="course", lazy=True)


# Grade class
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)

    # Define foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

CORS(app)

# Index endpoint
@app.route("/")
def index():
    return jsonify({"message": "Welcome to myU"})



# Signup endpoint with image upload
@app.route("/signup", methods=["POST"])
async def signup():
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return (
            jsonify({"error": "Email already exists! Please choose a different one."}),
            400,
        )

    # Hash the password before storing it
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    # handel and save the user's image
    if "file" in request.files:
        file = request.files["file"]
        new_img_name = handle_uploaded_file(file, app.config["UPLOAD_FOLDER"])
    else:
        new_img_name = 'default.jpg'

    # Add new user to the database
    new_user = User(email=email, hashed_pw=hashed_pw, img=new_img_name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {
            "message": f"Successfully signed up! Welcome, {email}.",
            "redirect": "login.html",
        }
    )


from sqlalchemy.exc import DatabaseError


# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.hashed_pw, password):
            # Generate JWT token
            # Using jwt library
            # token = jwt.encode(
            #     {
            #         "user_id": user.id,
            #         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            #     },
            #     app.config["JWT_SECRET_KEY"],
            #     algorithm="HS256",
            # )

            # Create an access token for the user
            # Using Flask-JWT-Extended
            # global conf added at the top
            access_token = create_access_token(identity=user.id)


            # Fetch additional information for the account.html
            user_info = {
                "email": user.email,
                "img_url": f"http://localhost:5000/{app.config["UPLOAD_FOLDER"]}/{user.img}",
                "username": user.username,
                "courses": [],  # List to store course information
                "scores": [],
                "token": access_token,
            }
            # Populate the courses and grades based on your data model
            for grade in user.grades:
                score = {
                    "course_name": grade.course.name,
                    "score": grade.score,
                }
                user_info["courses"].append(grade.course.name)
                user_info["scores"].append(score)
            return jsonify(user_info)

        return jsonify({"error": "Invalid email or password. Please try again."}), 401

    except DatabaseError as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


# Logout endpoint
@app.route("/logout")
@jwt_required
def logout():
    return jsonify({"message": "You have been logged out."})


import os


# Update the /update_account endpoint
@app.route("/update_account", methods=["POST"])
@jwt_required()
def update_account():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get the new username from the request form data
    new_username = request.form.get("username")
    if new_username:
        user.username = new_username

    # Check if a new image file is provided
    if "file" in request.files:
        old_img_name = user.img  # Get the old image path for deletion
        file = request.files["file"]
        new_img_name = handle_uploaded_file(file, app.config["UPLOAD_FOLDER"])

        if old_img_name and os.path.exists(f'{app.config["UPLOAD_FOLDER"]}/{old_img_name}'):
            os.remove(f'{app.config["UPLOAD_FOLDER"]}/{old_img_name}')  # Delete the old image file

        user.img = new_img_name

    db.session.commit()

    access_token = create_access_token(identity=user.id)
    # Return the updated user details in the response
    user_info = {
        "email": user.email,
        "img_url": f'http://localhost:5000/static/images/uploads/{user.img}',
        "username": user.username,
        "courses": [],
        "scores": [],
        "token": access_token,
    }

    for grade in user.grades:
        score = {"course_name": grade.course.name, "score": grade.score}
        user_info["courses"].append(grade.course.name)
        user_info["scores"].append(score)

    return jsonify(user_info)


@app.route("/delete_account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted successfully"}), 200





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
