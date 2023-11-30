from datetime import datetime
from models import Booking

class BookingManager:
    def __init__(self, db):
        self.db = db

    def is_room_available(self, room_id, checkin_date, checkout_date):
        existing_booking = Booking.query.filter(
            Booking.room_id == room_id,
            (
                (Booking.checkin_date <= checkin_date) & (Booking.checkout_date >= checkin_date) |
                (Booking.checkin_date <= checkout_date) & (Booking.checkout_date >= checkout_date) |
                (Booking.checkin_date >= checkin_date) & (Booking.checkout_date <= checkout_date)
            )
        ).first()

        return not existing_booking

    def book_room(self, guest_name, room_id, num_guests, checkin_date, checkout_date):
        new_booking = Booking(
            guest_name=guest_name,
            room_id=room_id,
            num_guests=num_guests,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )

        self.db.session.add(new_booking)
        self.db.session.commit()
