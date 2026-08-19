"""Regression checks for API validation and donor-privacy rules.

Run against a live server (python app.py) with: python validation_checks.py
Test records are removed at the end, so it is safe to re-run.
"""
import http.client
import json

PASS = "PASS"
FAIL = "FAIL"
TEST_EMAIL = "verify.person@example.com"
TEST_PATIENT = "Verify Patient"

results = []


def call(method, path, payload=None):
    conn = http.client.HTTPConnection("127.0.0.1", 5000, timeout=20)
    body = json.dumps(payload) if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    raw = response.read().decode()
    conn.close()
    try:
        return response.status, json.loads(raw)
    except json.JSONDecodeError:
        return response.status, raw[:120]


def check(name, condition, detail):
    results.append((PASS if condition else FAIL, name, detail))


def donor(**overrides):
    payload = {
        "name": "Verify Person",
        "blood_group": "O+",
        "phone": "+91 9111100000",
        "email": TEST_EMAIL,
        "age": 30,
        "date_of_birth": "1996-01-15",
        "city": "VerifyCity",
        "district": "VerifyDistrict",
        "country": "India",
    }
    payload.update(overrides)
    return payload


def blood_request(**overrides):
    payload = {
        "patient_name": TEST_PATIENT,
        "blood_group": "O+",
        "city": "VerifyCity",
        "district": "VerifyDistrict",
        "contact_phone": "+91 8000011111",
        "urgency": "critical",
    }
    payload.update(overrides)
    return payload


def run_checks():
    status, data = call("POST", "/api/donors", donor(email="not-an-email"))
    check("malformed email rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/donors", donor(age=7, date_of_birth="2019-01-15"))
    check("under-age donor rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/donors", donor(age=25, date_of_birth="2021-05-05"))
    check("age/DOB mismatch rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/donors", donor(date_of_birth="2400-01-01"))
    check("future DOB rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/donors", donor(blood_group="BANANA"))
    check("invalid blood group rejected", status == 400, f"{status}: {data.get('error')}")

    status, first = call("POST", "/api/donors", donor())
    status2, second = call("POST", "/api/donors", donor(name="Same Person Again"))
    check("valid donor accepted", status == 201, f"{status}: {first.get('message')}")
    check("duplicate donor rejected", status2 == 409, f"{status2}: {second.get('error')}")

    _, encoded = call("GET", "/api/donors/search?city=VerifyCity&blood_group=O%2B")
    _, raw_plus = call("GET", "/api/donors/search?city=VerifyCity&blood_group=O+")
    check(
        "unencoded '+' matches same donors",
        encoded.get("count") == raw_plus.get("count") == 1,
        f"encoded={encoded.get('count')} raw={raw_plus.get('count')}",
    )

    status, data = call("GET", "/api/donors/search?blood_group=BANANA")
    check("invalid search group rejected", status == 400, f"{status}: {data.get('error')}")

    _, data = call("GET", "/api/donors/search?city=VerifyCity&blood_group=O%2B")
    record = (data.get("donors") or [{}])[0]
    leaked = set(record.keys()) & {"phone", "email", "date_of_birth", "age"}
    check("public search hides contact data", not leaked, f"fields={sorted(record.keys())}")
    check("public search masks surname", record.get("name") == "Verify P.", f"name={record.get('name')}")

    status, _ = call("GET", "/api/notifications")
    check("public notifications endpoint removed", status == 404, f"status={status}")

    status, data = call("POST", "/api/food-log", {"restaurant_id": "abc", "description": "x", "quantity": "1"})
    check("non-numeric restaurant_id rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/blood-requests", blood_request(urgency="whenever"))
    check("invalid urgency rejected", status == 400, f"{status}: {data.get('error')}")

    status, data = call("POST", "/api/blood-requests", blood_request(contact_phone="12"))
    check("short contact phone rejected", status == 400, f"{status}: {data.get('error')}")

    _, created = call("POST", "/api/blood-requests", blood_request())
    check("blood request notifies donor", created.get("notifications_sent") == 1, str(created.get("notifications_sent")))

    _, notes = call("GET", "/api/admin/notifications")
    note_id = notes[0]["id"] if isinstance(notes, list) and notes else 0
    before = call("GET", "/api/admin/stats")[1].get("unread_notifications")
    status, _ = call("POST", f"/api/admin/notifications/{note_id}/read")
    after = call("GET", "/api/admin/stats")[1].get("unread_notifications")
    check("notification can be marked read", status == 200 and after == before - 1, f"unread {before} -> {after}")

    status, _ = call("POST", "/api/admin/notifications/999999/read")
    check("missing notification returns 404", status == 404, f"status={status}")


def cleanup():
    from app import app
    from models import BloodRequest, Donor, Notification, db

    with app.app_context():
        donors = Donor.query.filter(func_lower_email(Donor) == TEST_EMAIL).all()
        requests = BloodRequest.query.filter_by(patient_name=TEST_PATIENT).all()

        removed = 0
        for row in donors:
            removed += Notification.query.filter_by(recipient_type="donor", recipient_id=row.id).delete()
        for row in requests:
            removed += Notification.query.filter_by(
                notification_type="blood_request", related_entity_id=row.id
            ).delete()
        for row in donors + requests:
            db.session.delete(row)
        db.session.commit()
        print(f"\nCleanup: removed {len(donors)} donors, {len(requests)} requests, {removed} notifications.")


def func_lower_email(model):
    from sqlalchemy import func

    return func.lower(model.email)


if __name__ == "__main__":
    run_checks()
    print()
    for outcome, name, detail in results:
        print(f"{outcome}  {name}: {detail}")
    failures = [name for outcome, name, _ in results if outcome == FAIL]
    print("\nAll checks passed." if not failures else f"\nFailing: {failures}")
    cleanup()
