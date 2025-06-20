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


def test_add_product():
    url = f"{BASE_URL}/api/add_product"

    # Valid product insertion
    valid_payload = {
        "seller_id": "6aunogko@nittybiz.com",
        "category": "Bath Robes",
        "product_title": "A bath robe",
        "product_name": "Logitech PROMETHEUS bath robe",
        "product_description": "Compact wireless mouse with USB receiver",
        "quantity": "15",
        "price": "19.99",
        "status": "available"
    }
    response = requests.post(url, data=valid_payload)
    print("Valid Product Test - Status Code:", response.status_code)
    print("Valid Product Test - Response Text:", response.text)
    print()

    # invalid product insertion - invalid email
    invalid_payload = {
        "seller_id": "fake@email.com",
        "category": "Bath Robes",
        "product_title": "A bath robe",
        "product_name": "Logitech PROMETHEUS bath robe",
        "product_description": "Compact wireless mouse with USB receiver",
        "quantity": "15",
        "price": "19.99",
        "status": "available"
    }

    response = requests.post(url, data=invalid_payload)
    print("Invalid Product Test - Status Code:", response.status_code)
    print("Invalid Product Test - Response Text:", response.text)
    print()


# test for prod_by_cat endpoint
def test_prod_by_cat():
    url = f"{BASE_URL}/api/prod_by_cat"
    payload = {
        "category": "Bath Robes"
    }
    response = requests.post(url, data=payload)
    print("prod_by_cat - Status Code:", response.status_code)
    print("prod_by_cat - Response Text:", response.text)
    print()

# test for prod_by_seller endpoint
def test_prod_by_seller():
    url = f"{BASE_URL}/api/prod_by_seller"
    payload = {
        "seller_id": "gfwebr11@nittybiz.com"
    }
    response = requests.post(url, data=payload)
    print("prod_by_seller - Status Code:", response.status_code)
    print("prod_by_seller - Response Text:", response.text)
    print()

# get avg rating of some seller
def test_get_avg_seller_rating():
    url = f"{BASE_URL}/api/get_avg_seller_rating"
    payload = {
        "seller_id": "03vth6xl@nittybiz.com"
    }
    response = requests.post(url, data=payload)
    print("get_avg_seller_rating - Status Code:", response.status_code)
    print("get_avg_seller_rating - Response Text:", response.text)
    print()

# test for new_prod_review endpoint
def test_new_prod_review():
    url = f"{BASE_URL}/api/new_prod_review"
    payload = {
        "order_id": "846123",
        "review_desc": "Great product, would buy again!",
        "rating": "5"
    }
    response = requests.post(url, data=payload)
    print("new_prod_review - Status Code:", response.status_code)
    print("new_prod_review - Response Text:", response.text)
    print()

# test for get_listing_reviews endpoint
def test_get_listing_reviews():
    url = f"{BASE_URL}/api/get_listing_reviews"
    payload = {
        "listing_id": "16"
    }
    response = requests.post(url, data=payload)
    print("get_listing_reviews - Status Code:", response.status_code)
    print("get_listing_reviews - Response Text:", response.text)
    print()

# test for update_listing endpoint
def test_update_listing():
    url = f"{BASE_URL}/api/product_update"
    payload = {
        "seller_email": "dcjdw3qn@nittybiz.com",
        "listing_id": "2505",
        "product_price": "1999",   # this should be the new price * 100
        "quantity": "42"
    }
    response = requests.post(url, data=payload)
    print("update_listing    - Status Code:", response.status_code)
    print("update_listing    - Response Text:", response.text)
    print()

# test for order placement
def test_place_order():
    url = f"{BASE_URL}/api/place_order"
    payload = {
        "listing_id":   "747",
        "seller_email": "ztolk7z1@nittybiz.com",
        "buyer_id": "o5mrsfw0@nittybiz.com",
        "quantity":     "1",
        "price":        "50.00"
    }
    response = requests.post(url, data=payload)
    print("place_order      - Status Code:", response.status_code)
    print("place_order      - Response Text:", response.text)
    print()

    payload = {
        "listing_id":   "747",
        "seller_email": "ztolk7z1@nittybiz.com",
        "buyer_id": "o5mrsfw0@nittybiz.com",
        "quantity":     "6",
        "price":        "50.00"
    }
    response = requests.post(url, data=payload)
    print("place_order      - Status Code:", response.status_code)
    print("place_order      - Response Text:", response.text)
    print()

#test address key gen
def test_add_address():
    url = f"{BASE_URL}/api/add_address"
    payload = {
        "zipcode":     "16803",
        "street_num":  "432",
        "street_name": "Ablewood"
    }
    response = requests.post(url, data=payload)
    print("add_address     - Status Code:", response.status_code)
    print("add_address     - Response Text:", response.text)
    print()

if __name__ == "__main__":
    # Uncomment specific tests when running

    # test_login_generic()
    # test_login_specific()
    # test_complete_request()
    # test_get_requests()
    # test_top_level_categories()
    # test_get_categories_by_parent()
    # test_add_product()
    # test_prod_by_cat()
    # test_prod_by_seller()
    # test_get_avg_seller_rating()
    # test_new_prod_review()
    # test_get_listing_reviews()
    # test_update_listing()
    # test_place_order()
    test_add_address()