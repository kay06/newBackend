from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import bcrypt
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

#Users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable=False)
    admin_status = db.Column(db.Boolean, default=False)


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'email', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Ticket table
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.String(400))
    status = db.Column(db.String(100)) 

    def __init__(self, user_id, title, description, status):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.status = status

class TicketSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'title', 'description', 'status')

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

#post log in user to route /login
@app.route('/login', methods=["POST"])
def login():    
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return "Missing email or password", 400

    user = db.session.query(User).filter(User.email == email).first()

    if not user:
        return "User does not exist", 401

    user_stored_password = user.password

    given_password = password.encode('utf-8')  

    if bcrypt.checkpw(given_password, user_stored_password):
        return "Logged in successfully"

    return "Invalid email or password", 401

#post new user to route /new_user
@app.route('/new_user', methods=["POST"])
def add_user():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already Registered'}), 400

    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt) 

    new_user = User(name, email, hash)

    db.session.add(new_user)
    db.session.commit()


    user = User.query.get(new_user.id)

    return user_schema.jsonify(user)

#post new ticket made to route /new_ticket 
@app.route('/new_ticket', methods=["POST"])
def add_ticket():
    user_id = request.json['user_id']

    title = request.json['title']
    description = request.json['description']
    status = "new"

    new_ticket = Ticket(user_id, title, description, status)

    db.session.add(new_ticket)
    db.session.commit()

    ticket = Ticket.query.get(new_ticket.id)

    return ticket_schema.jsonify(ticket)

#put edited ticket to route /edit_ticket/<id> 
@app.route('/edit_ticket/<id>', methods=["PUT"])
def edit_ticket(id):

    ticket = Ticket.query.get(id)
    
    new_status = request.json.get('status')
    
    ticket.status = new_status 

    db.session.commit()
    return ticket_schema.jsonify(ticket)


#delete ticket to route /delete_ticket/<id> 
@app.route("/delete_ticket/<id>", methods=["DELETE"])
def delete_ticket(id):
    ticket = Ticket.query.get(id)
    
    db.session.delete(ticket)
    db.session.commit()

    return "Ticket was successfully deleted"

#get ticket to route /ticket/<id> 
@app.route("/ticket/<id>", methods=["GET"])
def get_ticket(id):
    ticket_id = Ticket.query.get(id)
    ticket_array = [ticket_id]
    return ticket_schema.jsonify(ticket_id)

#get all tickets to route /tickets
@app.route("/tickets", methods=["GET"])
def get_tickets():
    all_tickets = Ticket.query.all()
    result = tickets_schema.dump(all_tickets)
    print(result)
    return jsonify(result)

if __name__ == '__main__': 
    with app.app_context():
        db.create_all()
    app.run(debug=True)