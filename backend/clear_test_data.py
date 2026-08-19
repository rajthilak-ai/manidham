"""Remove records created by smoke_test.py, leaving real and seed data intact."""
from app import app
from models import BloodRequest, Donor, FoodLog, Institution, Notification, db

TEST_DONOR_EMAIL = "test.donor@example.com"
TEST_PATIENT_NAME = "Patient A"
TEST_FOOD_DESCRIPTION = "40 veg meals"


def main():
    with app.app_context():
        donors = Donor.query.filter_by(email=TEST_DONOR_EMAIL).all()
        requests = BloodRequest.query.filter_by(patient_name=TEST_PATIENT_NAME).all()
        logs = FoodLog.query.filter_by(description=TEST_FOOD_DESCRIPTION).all()
        institutions = Institution.query.filter_by(email="sunrise@example.com").all()

        removed_notifications = 0
        for donor in donors:
            removed_notifications += Notification.query.filter_by(
                recipient_type="donor", recipient_id=donor.id
            ).delete()
        for item in requests:
            removed_notifications += Notification.query.filter_by(
                notification_type="blood_request", related_entity_id=item.id
            ).delete()
        for log in logs:
            removed_notifications += Notification.query.filter_by(
                notification_type="food_available", related_entity_id=log.id
            ).delete()
        for institution in institutions:
            removed_notifications += Notification.query.filter_by(
                recipient_type="institution", recipient_id=institution.id
            ).delete()

        for group in (donors, requests, logs, institutions):
            for row in group:
                db.session.delete(row)

        db.session.commit()

        print(
            f"Removed {len(donors)} donors, {len(requests)} blood requests, "
            f"{len(logs)} food logs, {len(institutions)} institutions, "
            f"{removed_notifications} notifications."
        )
        print(
            f"Remaining -> donors: {Donor.query.count()}, "
            f"institutions: {Institution.query.count()}, "
            f"notifications: {Notification.query.count()}"
        )


if __name__ == "__main__":
    main()
