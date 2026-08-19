from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=False, index=True)
    country = db.Column(db.String(80), nullable=False, default="India")
    is_international = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "email": self.email,
            "age": self.age,
            "date_of_birth": self.date_of_birth.isoformat(),
            "city": self.city,
            "district": self.district,
            "country": self.country,
            "is_international": self.is_international,
            "created_at": self.created_at.isoformat(),
        }


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    contact_person = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food_logs = db.relationship("FoodLog", backref="restaurant", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "district": self.district,
            "created_at": self.created_at.isoformat(),
        }


class Institution(db.Model):
    __tablename__ = "institutions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    contact_person = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=False, index=True)
    institution_type = db.Column(db.String(30), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "district": self.district,
            "institution_type": self.institution_type,
            "created_at": self.created_at.isoformat(),
        }


class FoodLog(db.Model):
    __tablename__ = "food_logs"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "restaurant_id": self.restaurant_id,
            "restaurant_name": self.restaurant.name if self.restaurant else None,
            "description": self.description,
            "quantity": self.quantity,
            "city": self.city,
            "district": self.district,
            "created_at": self.created_at.isoformat(),
        }


class BloodRequest(db.Model):
    __tablename__ = "blood_requests"

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    city = db.Column(db.String(80), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=False, index=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    hospital = db.Column(db.String(160))
    urgency = db.Column(db.String(20), default="urgent")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_name": self.patient_name,
            "blood_group": self.blood_group,
            "city": self.city,
            "district": self.district,
            "contact_phone": self.contact_phone,
            "hospital": self.hospital,
            "urgency": self.urgency,
            "created_at": self.created_at.isoformat(),
        }


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(40), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recipient_type = db.Column(db.String(30), nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)
    related_entity_id = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "notification_type": self.notification_type,
            "message": self.message,
            "recipient_type": self.recipient_type,
            "recipient_id": self.recipient_id,
            "related_entity_id": self.related_entity_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
