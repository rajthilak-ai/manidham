"""End-to-end smoke test for the Manidham API. Run while app.py is serving."""
import http.client
import json


def call(method, path, payload=None):
    conn = http.client.HTTPConnection("127.0.0.1", 5000, timeout=10)
    body = json.dumps(payload) if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    conn.close()
    return response.status, data


def main():
    checks = []

    status, data = call("GET", "/api/health")
    checks.append(("health", status == 200, data))

    donor = {
        "name": "Test Donor",
        "blood_group": "B+",
        "phone": "+91 9999911111",
        "email": "test.donor@example.com",
        "age": 30,
        "date_of_birth": "1996-01-15",
        "city": "Madurai",
        "district": "Madurai",
        "country": "India",
        "is_international": False,
    }
    status, data = call("POST", "/api/donors", donor)
    # 409 means a previous run's donor is still present, which is fine for the
    # checks that follow.
    checks.append(("create donor", status in (201, 409), data.get("message") or data.get("error")))

    status, data = call("GET", "/api/donors/search?city=Madurai&blood_group=B%2B")
    checks.append(("search donors", data.get("count", 0) >= 1, f"{data.get('count')} found"))

    blood_request = {
        "patient_name": "Patient A",
        "blood_group": "B+",
        "city": "Madurai",
        "district": "Madurai",
        "contact_phone": "+91 8888822222",
    }
    status, data = call("POST", "/api/blood-requests", blood_request)
    checks.append(
        ("blood request notifies donors", data.get("notifications_sent", 0) >= 1,
         f"{data.get('notifications_sent')} donors notified")
    )

    restaurants = call("GET", "/api/admin/restaurants")[1]
    restaurant_id = restaurants[0]["id"] if restaurants else None
    status, data = call(
        "POST", "/api/food-log",
        {"restaurant_id": restaurant_id, "description": "40 veg meals", "quantity": "40 meals"},
    )
    checks.append(
        ("food log notifies institutions", data.get("notifications_sent", 0) >= 1,
         f"{data.get('notifications_sent')} institutions notified")
    )

    status, data = call("POST", "/api/donors", {"name": "Incomplete"})
    checks.append(("validation rejects bad input", status == 400, data.get("error")))

    status, stats = call("GET", "/api/admin/stats")
    checks.append(("admin stats", status == 200, stats))

    for name, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'}  {name}: {detail}")

    failures = [name for name, passed, _ in checks if not passed]
    print("\nAll checks passed." if not failures else f"\nFailed: {failures}")


if __name__ == "__main__":
    main()
