import re
import bcrypt
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configuration for the database and session
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/your_db_name'
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask sessions
db = SQLAlchemy(app)

# --------------------------
# Helper Functions
# --------------------------

def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password_hash(hashed_password: str, password: str) -> bool:
    """
    Verifies a plain-text password against the hashed version.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# --------------------------
# Database Models
# --------------------------

class User(db.Model):
    """
    Defines the User model for SQLAlchemy.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


# --------------------------
# Example Usage of Functions
# --------------------------

@app.route('/register', methods=['POST'])
def register():
    """
    Example user registration route.
    """
    username = "example_user"
    email = "user@example.com"
    password = "securepassword"

    # Validate email
    if not is_valid_email(email):
        return "Invalid email address", 400

    # Hash the password
    hashed_password = hash_password(password)

    # Create a new user instance
    new_user = User(username=username, email=email, password=hashed_password)

    # Add to the database
    db.session.add(new_user)
    db.session.commit()

    return "User registered successfully", 201


@app.route('/login', methods=['POST'])
def login():
    """
    Example login route.
    """
    username = "example_user"
    password = "securepassword"

    # Query user by username
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password matches
    if user and check_password_hash(user.password, password):
        # Start session
        session['user_id'] = user.id
        return "Login successful", 200
    else:
        return "Invalid credentials", 401


if __name__ == '__main__':
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run(debug=True)