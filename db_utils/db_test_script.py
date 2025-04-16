import requests

BASE_URL = "http://127.0.0.1:5000"

#testing incorrect user/pword
def test_login_generic():
    url = f"{BASE_URL}/api/users"
    payload = {"email": "your_username", "password": "your_password"}

    response = requests.post(url, data=payload)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    print()

# testing a good login the password IS ALREADY HASHED.
def test_login_specific():
    url = f"{BASE_URL}/api/users"
    payload = {
        "email": "o5mrsfw0@nittybiz.com",
        "password": "9057bc90227bb3025b8e2a4049763407678525e5165192e463c27871af3f2893"
    }

    response = requests.post(url, data=payload)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    print()

# testing active requests endpoint
def test_get_requests():
    url = f"{BASE_URL}/api/get_active_requests"
    response = requests.post(url)

    print("Status Code:", response.status_code)
    try:
        print("Response JSON:")
        print(response.json())
    except ValueError:
        print("Invalid JSON Response:")
        print(response.text)
    print()

# testing status update for requests - no code to reset request 104, so you have to reset the db as of now to fix it
def test_complete_request():
    url = f"{BASE_URL}/api/complete_request"
    payload = {
        "request_id": "104"
    }

    response = requests.post(url, data=payload)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    print()

def test_top_level_categories():
    url = f"{BASE_URL}/api/top_level_categories"
    # This endpoint doesn't expect any payload data.
    response = requests.post(url)

    print("== Test Top Level Categories ==")
    print("Status Code:", response.status_code)
    print("Response Text:")
    print(response.text)
    print()


def test_get_categories_by_parent():
    url = f"{BASE_URL}/api/child_categories"

    # First test with "Dog" as the category
    payload1 = {"category": "Dog"}
    response1 = requests.post(url, data=payload1)
    print("Status Code:", response1.status_code)
    try:
        print("Response JSON:")
        print(response1.json())
    except ValueError:
        print("Invalid JSON Response:")
        print(response1.text)
    print()

    # Then test with "Dog Dry Food" as the category
    payload2 = {"category": "Dog Dry Food"}
    response2 = requests.post(url, data=payload2)
    print("Status Code:", response2.status_code)
    try:
        print("Response JSON:")
        print(response2.json())
    except ValueError:
        print("Invalid JSON Response:")
        print(response2.text)
    print()


if __name__ == "__main__":
    # Uncomment specific tests when running

    # test_login_generic()
    # test_login_specific()
    # test_complete_request()
    # test_get_requests()
    # test_top_level_categories()
    test_get_categories_by_parent()