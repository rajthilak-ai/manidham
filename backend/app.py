import os
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from models import BloodRequest, Donor, FoodLog, GalleryImage, Institution, Notification, Restaurant, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "manidham.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "gallery")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "manidham-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB per upload (videos are larger)

CORS(app)
db.init_app(app)

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GALLERY_CATEGORIES = {"general", "education", "blood", "food"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}
ALLOWED_MEDIA_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "manidham@admin")
ADMIN_TOKEN_MAX_AGE = 8 * 60 * 60  # 8 hours

admin_token_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="manidham-admin-token")


def generate_admin_token(username):
    return admin_token_serializer.dumps({"username": username})


def verify_admin_token(token):
    try:
        data = admin_token_serializer.loads(token, max_age=ADMIN_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("username")


def require_admin(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else None
        username = verify_admin_token(token) if token else None
        if not username:
            return jsonify({"error": "Invalid or expired session"}), 401
        request.admin_username = username
        return handler(*args, **kwargs)

    return wrapper


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def allowed_media_file(filename):
    return get_file_extension(filename) in ALLOWED_MEDIA_EXTENSIONS


def media_type_for_extension(extension):
    return "video" if extension in ALLOWED_VIDEO_EXTENSIONS else "image"


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def validate_required(data, fields):
    missing = [field for field in fields if not str(data.get(field, "")).strip()]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None


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

    if data["blood_group"] not in BLOOD_GROUPS:
        return jsonify({"error": "Invalid blood group"}), 400

    try:
        dob = parse_date(data["date_of_birth"])
        age = int(data["age"])
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age or date of birth"}), 400

    donor = Donor(
        name=data["name"].strip(),
        blood_group=data["blood_group"],
        phone=data["phone"].strip(),
        email=data["email"].strip(),
        age=age,
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
    blood_group = request.args.get("blood_group", "").strip()

    if not blood_group:
        return jsonify({"error": "Blood group is required for search"}), 400

    query = Donor.query.filter(Donor.blood_group == blood_group)

    if city:
        query = query.filter(func.lower(Donor.city) == city.lower())
    if district:
        query = query.filter(func.lower(Donor.district) == district.lower())

    donors = query.order_by(Donor.created_at.desc()).all()
    return jsonify({"count": len(donors), "donors": [donor.to_dict() for donor in donors]})


@app.route("/api/restaurants", methods=["POST"])
def create_restaurant():
    data = request.get_json(silent=True) or {}
    error = validate_required(
        data,
        ["name", "contact_person", "phone", "email", "address", "city", "district"],
    )
    if error:
        return jsonify({"error": error}), 400

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

    restaurant = db.session.get(Restaurant, data["restaurant_id"])
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

    if data["blood_group"] not in BLOOD_GROUPS:
        return jsonify({"error": "Invalid blood group"}), 400

    blood_request = BloodRequest(
        patient_name=data["patient_name"].strip(),
        blood_group=data["blood_group"],
        city=data["city"].strip(),
        district=data["district"].strip(),
        contact_phone=data["contact_phone"].strip(),
        hospital=data.get("hospital", "").strip() or None,
        urgency=data.get("urgency", "urgent"),
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


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"token": generate_admin_token(username), "username": username})


@app.route("/api/admin/verify", methods=["GET"])
@require_admin
def admin_verify():
    return jsonify({"username": request.admin_username})


@app.route("/api/gallery", methods=["GET"])
def list_gallery():
    category = request.args.get("category", "").strip().lower()
    query = GalleryImage.query
    if category:
        query = query.filter(GalleryImage.category == category)
    images = query.order_by(GalleryImage.created_at.desc()).all()
    return jsonify({"count": len(images), "images": [image.to_dict() for image in images]})


@app.route("/api/gallery", methods=["POST"])
@require_admin
def upload_gallery_image():
    file = request.files.get("file") or request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400
    if not allowed_media_file(file.filename):
        return jsonify(
            {"error": "Unsupported file type. Use PNG/JPG/GIF/WEBP for photos or MP4/WEBM/MOV/OGG for videos"}
        ), 400

    category = (request.form.get("category") or "general").strip().lower()
    if category not in GALLERY_CATEGORIES:
        category = "general"
    caption = (request.form.get("caption") or "").strip() or None

    extension = get_file_extension(file.filename)
    stored_name = secure_filename(f"{uuid.uuid4().hex}.{extension}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file.save(os.path.join(UPLOAD_DIR, stored_name))

    image = GalleryImage(
        filename=stored_name,
        media_type=media_type_for_extension(extension),
        caption=caption,
        category=category,
        uploaded_by=request.admin_username,
    )
    db.session.add(image)
    db.session.commit()
    return jsonify({"message": "Media uploaded", "image": image.to_dict()}), 201


@app.route("/api/gallery/<int:image_id>", methods=["DELETE"])
@require_admin
def delete_gallery_image(image_id):
    image = db.session.get(GalleryImage, image_id)
    if not image:
        return jsonify({"error": "Image not found"}), 404

    file_path = os.path.join(UPLOAD_DIR, image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Image deleted"})


@app.route("/api/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/notifications", methods=["GET"])
def list_notifications():
    recipient_type = request.args.get("recipient_type")
    recipient_id = request.args.get("recipient_id", type=int)

    query = Notification.query
    if recipient_type:
        query = query.filter(Notification.recipient_type == recipient_type)
    if recipient_id:
        query = query.filter(Notification.recipient_id == recipient_id)

    notifications = query.order_by(Notification.created_at.desc()).limit(100).all()
    return jsonify({"count": len(notifications), "notifications": [n.to_dict() for n in notifications]})


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
            "gallery_images": GalleryImage.query.count(),
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


def ensure_gallery_media_type_column():
    inspector = db.inspect(db.engine)
    if "gallery_images" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("gallery_images")}
    if "media_type" not in columns:
        with db.engine.begin() as connection:
            connection.execute(
                db.text("ALTER TABLE gallery_images ADD COLUMN media_type VARCHAR(10) DEFAULT 'image'")
            )


with app.app_context():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    db.create_all()
    ensure_gallery_media_type_column()
    seed_sample_data()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
