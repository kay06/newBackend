from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from faker import Faker
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import re
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        # Hash the password before storing it
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # Verify the hashed password
        return check_password_hash(self.password, password)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password')
        ordered = True

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

@app.route('/user', methods=['POST'])
def add_user():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not validate_email(email):
        return make_response(jsonify({"message": "Invalid email"}), 400)

    if len(password) < 8:
        return make_response(jsonify({"message": "Password must be at least 8 characters long"}), 400)

    new_user = User(email, password)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    return multiple_user_schema.jsonify(users)

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return make_response(jsonify({"message": "User not found"}), 404)

    db.session.delete(user)
    db.session.commit()
    return {'message': 'User deleted successfully'}

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return make_response(jsonify({"message": "Email and password are required"}), 400)

    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response(jsonify({"message": "Invalid credentials"}), 401)

    if not user.check_password(password):
        return make_response(jsonify({"message": "Invalid credentials"}), 401)

    # Generate JWT token
    jwt_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    }
    jwt_token = jwt.encode(jwt_payload, 'your_secret_key', algorithm='HS256')

    return jsonify({"message": "Login successful", "token": jwt_token})

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return make_response(jsonify({"message": "User not found"}), 404)

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not validate_email(email):
        return make_response(jsonify({"message": "Invalid email"}), 400)

    if len(password) < 8:
        return make_response(jsonify({"message": "Password must be at least 8 characters long"}), 400)

    user.email = email
    user.set_password(password)
    db.session.commit()

    return user_schema.jsonify(user)

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"message": "Bad Request", "details": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Resource Not Found", "details": str(e)}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"message": "Internal Server Error", "details": str(e)}), 500

@app.route('/populate_users', methods=['GET'])
def populate_users():
    num_users = 10  # Number of fake users to add
    for _ in range(num_users):
        fake_email = Faker().email()
        fake_password = Faker().password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        new_user = User(fake_email, fake_password)
        db.session.add(new_user)
    db.session.commit()
    return {'message': f'Successfully added {num_users} fake users'}

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    for rule in app.url_map.iter_rules():
        print(f"HTTP Endpoint: http://{host}:{port}{rule}")

    with app.app_context():
        db.create_all()
        populate_users()
    app.run(debug=True, host='127.0.0.1', port=5000)
