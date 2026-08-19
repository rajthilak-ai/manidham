import os
import re
from datetime import date, datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import func, or_

from models import BloodRequest, Donor, FoodLog, Institution, Notification, Restaurant, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "manidham.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "manidham-dev-secret")

CORS(app)
db.init_app(app)

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
URGENCY_LEVELS = {"routine", "urgent", "critical"}
MIN_DONOR_AGE = 18
MAX_DONOR_AGE = 65

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")
# Keeps digits and a single leading +, so numbers can be compared for duplicates
# regardless of how the user spaced or punctuated them.
PHONE_STRIP_PATTERN = re.compile(r"[^\d+]")


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def validate_required(data, fields):
    missing = [field for field in fields if not str(data.get(field, "")).strip()]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None


def is_valid_email(value):
    return bool(EMAIL_PATTERN.match(value.strip()))


def normalize_phone(value):
    return PHONE_STRIP_PATTERN.sub("", value or "")


def normalize_blood_group(value):
    """Accept a blood group even when '+' arrived as a space.

    An unencoded '+' in a query string decodes to a space, which would otherwise
    turn 'O+' into 'O ' and silently match no donors. Surrounding whitespace is
    the only signal that a '+' was lost, so it is checked before stripping.
    """
    raw = (value or "").upper()
    candidate = raw.strip()
    if candidate in BLOOD_GROUPS:
        return candidate

    positive = f"{candidate}+"
    if raw != candidate and positive in BLOOD_GROUPS:
        return positive
    return None


def age_from_date_of_birth(dob, today=None):
    today = today or date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def notify_institutions_for_food(food_log, restaurant):
    institutions = Institution.query.filter(
        func.lower(Institution.city) == food_log.city.lower(),
        func.lower(Institution.district) == food_log.district.lower(),
    ).all()

    for institution in institutions:
        message = (
            f"Food available from {restaurant.name}: {food_log.description} "
            f"({food_log.quantity}). Contact {restaurant.contact_person} at {restaurant.phone}."
        )
        notification = Notification(
            notification_type="food_available",
            message=message,
            recipient_type="institution",
            recipient_id=institution.id,
            related_entity_id=food_log.id,
        )
        db.session.add(notification)


def notify_donors_for_blood_request(blood_request):
    donors = Donor.query.filter(
        Donor.blood_group == blood_request.blood_group,
        or_(
            func.lower(Donor.city) == blood_request.city.lower(),
            func.lower(Donor.district) == blood_request.district.lower(),
        ),
    ).all()

    for donor in donors:
        message = (
            f"Urgent blood need: {blood_request.blood_group} for {blood_request.patient_name} "
            f"in {blood_request.city}, {blood_request.district}. "
            f"Contact {blood_request.contact_phone}."
        )
        notification = Notification(
            notification_type="blood_request",
            message=message,
            recipient_type="donor",
            recipient_id=donor.id,
            related_entity_id=blood_request.id,
        )
        db.session.add(notification)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Manidham API"})


@app.route("/api/donors", methods=["POST"])
def create_donor():
    data = request.get_json(silent=True) or {}
    error = validate_required(
        data,
        ["name", "blood_group", "phone", "email", "age", "date_of_birth", "city", "district", "country"],
    )
    if error:
        return jsonify({"error": error}), 400

    blood_group = normalize_blood_group(data["blood_group"])
    if not blood_group:
        return jsonify({"error": f"Blood group must be one of: {', '.join(BLOOD_GROUPS)}"}), 400

    email = data["email"].strip()
    if not is_valid_email(email):
        return jsonify({"error": "Enter a valid email address"}), 400

    phone = data["phone"].strip()
    if len(normalize_phone(phone)) < 8:
        return jsonify({"error": "Enter a valid phone number"}), 400

    try:
        dob = parse_date(data["date_of_birth"])
        claimed_age = int(data["age"])
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age or date of birth"}), 400

    if dob > date.today():
        return jsonify({"error": "Date of birth cannot be in the future"}), 400

    actual_age = age_from_date_of_birth(dob)
    if abs(actual_age - claimed_age) > 1:
        return jsonify(
            {"error": f"Age does not match date of birth (expected about {actual_age})"}
        ), 400

    if actual_age < MIN_DONOR_AGE or actual_age > MAX_DONOR_AGE:
        return jsonify(
            {"error": f"Donors must be between {MIN_DONOR_AGE} and {MAX_DONOR_AGE} years old"}
        ), 400

    existing = Donor.query.filter(
        or_(
            func.lower(Donor.email) == email.lower(),
            Donor.phone == phone,
        )
    ).first()
    if existing:
        return jsonify({"error": "A donor with this email or phone number is already enrolled"}), 409

    donor = Donor(
        name=data["name"].strip(),
        blood_group=blood_group,
        phone=phone,
        email=email,
        age=actual_age,
        date_of_birth=dob,
        city=data["city"].strip(),
        district=data["district"].strip(),
        country=data["country"].strip(),
        is_international=bool(data.get("is_international", False)),
    )
    db.session.add(donor)
    db.session.commit()
    return jsonify({"message": "Donor enrolled successfully", "donor": donor.to_dict()}), 201


@app.route("/api/donors/search", methods=["GET"])
def search_donors():
    city = request.args.get("city", "").strip()
    district = request.args.get("district", "").strip()
    # Left unstripped: trailing whitespace tells normalize_blood_group that an
    # unencoded '+' was decoded into a space.
    raw_group = request.args.get("blood_group", "")

    if not raw_group.strip():
        return jsonify({"error": "Blood group is required for search"}), 400

    blood_group = normalize_blood_group(raw_group)
    if not blood_group:
        return jsonify({"error": f"Blood group must be one of: {', '.join(BLOOD_GROUPS)}"}), 400

    query = Donor.query.filter(Donor.blood_group == blood_group)

    if city:
        query = query.filter(func.lower(Donor.city) == city.lower())
    if district:
        query = query.filter(func.lower(Donor.district) == district.lower())

    donors = query.order_by(Donor.created_at.desc()).all()
    # Contact details are deliberately withheld here: this endpoint is public, so
    # returning them would expose a scrapeable donor contact list. Requesters
    # submit a blood request instead, and matching donors are notified.
    return jsonify(
        {
            "count": len(donors),
            "donors": [donor.to_public_dict() for donor in donors],
            "contact_policy": "Submit an urgent blood request to notify these donors directly.",
        }
    )


@app.route("/api/restaurants", methods=["POST"])
def create_restaurant():
    data = request.get_json(silent=True) or {}
    error = validate_required(
        data,
        ["name", "contact_person", "phone", "email", "address", "city", "district"],
    )
    if error:
        return jsonify({"error": error}), 400

    if not is_valid_email(data["email"]):
        return jsonify({"error": "Enter a valid email address"}), 400

    restaurant = Restaurant(
        name=data["name"].strip(),
        contact_person=data["contact_person"].strip(),
        phone=data["phone"].strip(),
        email=data["email"].strip(),
        address=data["address"].strip(),
        city=data["city"].strip(),
        district=data["district"].strip(),
    )
    db.session.add(restaurant)
    db.session.commit()
    return jsonify({"message": "Restaurant enrolled successfully", "restaurant": restaurant.to_dict()}), 201


@app.route("/api/institutions", methods=["POST"])
def create_institution():
    data = request.get_json(silent=True) or {}
    error = validate_required(
        data,
        ["name", "contact_person", "phone", "email", "address", "city", "district", "institution_type"],
    )
    if error:
        return jsonify({"error": error}), 400

    if not is_valid_email(data["email"]):
        return jsonify({"error": "Enter a valid email address"}), 400

    institution_type = data["institution_type"].strip().lower().replace(" ", "_")
    if institution_type not in {"orphanage", "old_age_home"}:
        return jsonify({"error": "Institution type must be orphanage or old_age_home"}), 400

    institution = Institution(
        name=data["name"].strip(),
        contact_person=data["contact_person"].strip(),
        phone=data["phone"].strip(),
        email=data["email"].strip(),
        address=data["address"].strip(),
        city=data["city"].strip(),
        district=data["district"].strip(),
        institution_type=institution_type,
    )
    db.session.add(institution)
    db.session.commit()
    return jsonify({"message": "Institution enrolled successfully", "institution": institution.to_dict()}), 201


@app.route("/api/food-log", methods=["POST"])
def log_food():
    data = request.get_json(silent=True) or {}
    error = validate_required(data, ["restaurant_id", "description", "quantity"])
    if error:
        return jsonify({"error": error}), 400

    try:
        restaurant_id = int(data["restaurant_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "restaurant_id must be a number"}), 400

    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    food_log = FoodLog(
        restaurant_id=restaurant.id,
        description=data["description"].strip(),
        quantity=data["quantity"].strip(),
        city=restaurant.city,
        district=restaurant.district,
    )
    db.session.add(food_log)
    db.session.flush()
    notify_institutions_for_food(food_log, restaurant)
    db.session.commit()

    notifications = Notification.query.filter_by(
        notification_type="food_available", related_entity_id=food_log.id
    ).count()
    return jsonify(
        {
            "message": "Food logged and institutions notified",
            "food_log": food_log.to_dict(),
            "notifications_sent": notifications,
        }
    ), 201


@app.route("/api/blood-requests", methods=["POST"])
def create_blood_request():
    data = request.get_json(silent=True) or {}
    error = validate_required(
        data,
        ["patient_name", "blood_group", "city", "district", "contact_phone"],
    )
    if error:
        return jsonify({"error": error}), 400

    blood_group = normalize_blood_group(data["blood_group"])
    if not blood_group:
        return jsonify({"error": f"Blood group must be one of: {', '.join(BLOOD_GROUPS)}"}), 400

    contact_phone = data["contact_phone"].strip()
    if len(normalize_phone(contact_phone)) < 8:
        return jsonify({"error": "Enter a valid contact phone number"}), 400

    urgency = str(data.get("urgency", "urgent")).strip().lower()
    if urgency not in URGENCY_LEVELS:
        return jsonify({"error": f"Urgency must be one of: {', '.join(sorted(URGENCY_LEVELS))}"}), 400

    blood_request = BloodRequest(
        patient_name=data["patient_name"].strip(),
        blood_group=blood_group,
        city=data["city"].strip(),
        district=data["district"].strip(),
        contact_phone=contact_phone,
        hospital=data.get("hospital", "").strip() or None,
        urgency=urgency,
    )
    db.session.add(blood_request)
    db.session.flush()
    notify_donors_for_blood_request(blood_request)
    db.session.commit()

    notifications = Notification.query.filter_by(
        notification_type="blood_request", related_entity_id=blood_request.id
    ).count()
    return jsonify(
        {
            "message": "Blood request created and matching donors notified",
            "request": blood_request.to_dict(),
            "notifications_sent": notifications,
        }
    ), 201


@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    return jsonify(
        {
            "donors": Donor.query.count(),
            "restaurants": Restaurant.query.count(),
            "institutions": Institution.query.count(),
            "food_logs": FoodLog.query.count(),
            "blood_requests": BloodRequest.query.count(),
            "notifications": Notification.query.count(),
            "unread_notifications": Notification.query.filter_by(is_read=False).count(),
        }
    )


@app.route("/api/admin/donors", methods=["GET"])
def admin_donors():
    donors = Donor.query.order_by(Donor.created_at.desc()).all()
    return jsonify([donor.to_dict() for donor in donors])


@app.route("/api/admin/restaurants", methods=["GET"])
def admin_restaurants():
    restaurants = Restaurant.query.order_by(Restaurant.created_at.desc()).all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


@app.route("/api/admin/institutions", methods=["GET"])
def admin_institutions():
    institutions = Institution.query.order_by(Institution.created_at.desc()).all()
    return jsonify([institution.to_dict() for institution in institutions])


@app.route("/api/admin/food-logs", methods=["GET"])
def admin_food_logs():
    logs = FoodLog.query.order_by(FoodLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])


@app.route("/api/admin/blood-requests", methods=["GET"])
def admin_blood_requests():
    requests_list = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    return jsonify([item.to_dict() for item in requests_list])


@app.route("/api/admin/notifications", methods=["GET"])
def admin_notifications():
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(200).all()
    return jsonify([notification.to_dict() for notification in notifications])


@app.route("/api/admin/notifications/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    notification = db.session.get(Notification, notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read", "notification": notification.to_dict()})


def seed_sample_data():
    if Donor.query.count() > 0:
        return

    sample_donors = [
        Donor(
            name="Arun Kumar",
            blood_group="O+",
            phone="+91 9876543210",
            email="arun@example.com",
            age=28,
            date_of_birth=datetime(1998, 3, 12).date(),
            city="Chennai",
            district="Chennai",
            country="India",
        ),
        Donor(
            name="Sarah Mitchell",
            blood_group="A+",
            phone="+1 4155550199",
            email="sarah@example.com",
            age=32,
            date_of_birth=datetime(1994, 7, 21).date(),
            city="San Francisco",
            district="California",
            country="United States",
            is_international=True,
        ),
    ]
    db.session.add_all(sample_donors)

    restaurant = Restaurant(
        name="Spice Garden Hotel",
        contact_person="Ravi Menon",
        phone="+91 9123456780",
        email="contact@spicegarden.com",
        address="12 Anna Salai",
        city="Chennai",
        district="Chennai",
    )
    db.session.add(restaurant)

    institutions = [
        Institution(
            name="Hope Orphanage",
            contact_person="Meera Devi",
            phone="+91 9000012345",
            email="hope@example.com",
            address="45 Gandhi Nagar",
            city="Chennai",
            district="Chennai",
            institution_type="orphanage",
        ),
        Institution(
            name="Golden Years Home",
            contact_person="Joseph Thomas",
            phone="+91 9000098765",
            email="golden@example.com",
            address="78 Lake View Road",
            city="Chennai",
            district="Chennai",
            institution_type="old_age_home",
        ),
    ]
    db.session.add_all(institutions)
    db.session.commit()


with app.app_context():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db.create_all()
    seed_sample_data()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
