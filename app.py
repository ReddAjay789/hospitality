from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json

app = Flask(__name__)

# Configure your PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kugopkwzozqmxm:5b8f1c823816f558074907114bc198bf8888cd952179338773dc703ed6375bff@ec2-52-4-153-146.compute-1.amazonaws.com:5432/deaq1g38r9n337'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Replace this with the output of os.urandom

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define your Room and Booking models
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_urls = db.Column(db.JSON)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(255))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    num_guests = db.Column(db.Integer)
    checkin_date = db.Column(db.Date)
    checkout_date = db.Column(db.Date)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('bookingservice'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('bookingservice'))

@app.route('/')
@login_required
def bookingservice():
    if current_user.role.name:
        # Only show the list of rooms for users
        rooms = Room.query.all()
        rooms_with_images = []
        for room in rooms:
            room_dict = room.__dict__
            room_dict.pop('_sa_instance_state')  # Remove SQLAlchemy-specific attribute
            room_dict['images'] = json.loads(room_dict.pop('image_urls'))
            rooms_with_images.append(room_dict)

        return render_template('bookingservice.html', rooms=rooms_with_images)
    elif current_user.role.name == 'admin':
        # Show the full admin interface
        # You may want to implement a separate admin interface or modify the existing one
        return render_template('bookingservice.html')

@app.route('/api/room/<int:room_id>', methods=['GET'])
def get_room_details(room_id):
    room = Room.query.get(room_id)

    if room:
        room_details = {
            'id': room.id,
            'title': room.title,
            'description': room.description,
            'price': room.price,
            'images': room.image_urls if room.image_urls else []
        }
        return jsonify(room_details)
    else:
        return jsonify({'error': 'Room not found'}), 404

@app.route('/api/book-room', methods=['POST'])
@login_required
def book_a_room():
    try:
        data = request.get_json()
        app.logger.info('Received data: %s', data)

        guest_name = data.get('guestName')
        room_id = data.get('roomId')
        num_guests = data.get('numGuests')
        checkin_date = data.get('checkinDate')
        checkout_date = data.get('checkoutDate')

        # Validate data (you can add more validation as needed)
        if not (guest_name and room_id and num_guests and checkin_date and checkout_date):
            app.logger.error('Invalid input data')
            return jsonify({'error': 'Invalid input data'}), 400

        today_date = datetime.now().strftime('%Y-%m-%d')

        if checkout_date <= checkin_date:
            app.logger.error('Checkout date must be later than check-in date')
            return jsonify({'error': 'Checkout date must be later than check-in date'}), 400

        if checkin_date < today_date or checkout_date < today_date:
            app.logger.error('Check-in and check-out dates should not be earlier than today')
            return jsonify({'error': 'Check-in and check-out dates should not be earlier than today'}), 400

        # Check if the room is already booked for the specified date range
        existing_booking = Booking.query.filter(
            Booking.room_id == room_id,
            (
                (Booking.checkin_date <= checkin_date) & (Booking.checkout_date >= checkin_date) |
                (Booking.checkin_date <= checkout_date) & (Booking.checkout_date >= checkout_date) |
                (Booking.checkin_date >= checkin_date) & (Booking.checkout_date <= checkout_date)
            )
        ).first()

        if existing_booking:
            app.logger.error('Room already booked for the specified date range')
            return jsonify({'error': 'Room already booked for the specified date range'}), 400

        # Save booking to the database
        new_booking = Booking(
            guest_name=guest_name,
            room_id=room_id,
            num_guests=num_guests,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )

        db.session.add(new_booking)
        db.session.commit()

        app.logger.info('Booking successful!')
        return jsonify({'success': 'Room Booked Successfully'})
    except Exception as e:
        app.logger.error('An error occurred: %s', str(e))
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
