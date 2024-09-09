import re
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from typing import List
import bcrypt
from datetime import datetime

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/your_db_name'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User model definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Transaction model definition
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Transaction {self.amount} {self.category}>'

# User management functions
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

# Transaction management functions
def add_transaction(user_id: int, amount: float, category: str, date: str, description: str) -> bool:
    """
    Adds a new transaction (income/expense) to the database for a user.
    """
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        category=category,
        date=datetime.strptime(date, '%Y-%m-%d'),
        description=description
    )
    db.session.add(transaction)
    db.session.commit()
    return True

def get_transactions(user_id: int, start_date: str, end_date: str) -> List[Transaction]:
    """
    Retrieves all transactions within a date range for a specific user.
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    return Transaction.query.filter_by(user_id=user_id).filter(Transaction.date.between(start, end)).all()

def delete_transaction(transaction_id: int) -> bool:
    """
    Deletes a transaction based on its ID.
    """
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        return True
    return False

if __name__ == "__main__":
    # Run the Flask app (for testing purposes)
    app.run(debug=True)
