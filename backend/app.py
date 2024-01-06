from flask import Flask, jsonify, request, send_from_directory, url_for
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from image_handler import handle_uploaded_file

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myU.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ROOT_URL"] = "localhost:5000/"
app.config["UPLOAD_FOLDER"] = "static/images/uploads"
app.config["DEFAULT_IMG"] = "static/images/default.jpg"

app.secret_key = "devkey"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    img = db.Column(db.String(255), nullable=False)

    # Define one-to-many relationship with Grade
    grades = db.relationship("Grade", backref="user", lazy=True)

    def __init__(self, email, hashed_pw, img, username=None):
        self.email = email
        self.hashed_pw = hashed_pw
        self.img = img

        # Set the username based on the email if not provided
        self.username = username or self.get_username()

    def get_username(self):
        return self.email.split("@")[0]


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    # (Assuming you have a User model with an email field)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return (
            jsonify({"error": "Email already exists! Please choose a different one."}),
            400,
        )

    # Hash the password before storing it
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    # Upload and save the user's image
    if "file" in request.files:
        file = request.files["file"]
        img_path = handle_uploaded_file(file, app.config.UPLOAD_FOLDER)
    else:
        img_path = app.config["DEFAULT_IMG"]

    # Add new user to the database
    new_user = User(email=email, hashed_pw=hashed_pw, img=img_path)
    db.session.add(new_user)
    db.session.commit()

    # Log in the user after signing up
    login_user(new_user)

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
            login_user(user)

            # Fetch additional information for the account.html
            user_info = {
                "email": user.email,
                "img_url": f"http://localhost:5000/{user.img}",
                "username": user.get_username(),
                "courses": [],  # List to store course information
                "scores": [],
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
@login_required
def logout():
    logout_user()
    return jsonify({"message": "You have been logged out."})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
