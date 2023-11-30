from werkzeug.security import generate_password_hash

# Assuming you have a Flask app and SQLAlchemy models set up
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kugopkwzozqmxm:5b8f1c823816f558074907114bc198bf8888cd952179338773dc703ed6375bff@ec2-52-4-153-146.compute-1.amazonaws.com:5432/deaq1g38r9n337'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

# Function to generate hashed password
def generate_hashed_password(password):
    return generate_password_hash(password, method='sha256')

# Inserting a user with a hashed password
hashed_admin_password = generate_hashed_password('user@123$')

# Assuming 'admin' is the role with ID 1
admin_user = User(username='ajay_user', password=hashed_admin_password, role_id=2)
db.session.add(admin_user)
db.session.commit()


# username: ajay_user  password: user@123$
# username: admin   password: admin123