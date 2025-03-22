import requests

url = "http://127.0.0.1:5000/api/users"
payload = {"email": "your_username", "password": "your_password"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response Text:", response.text)

url = "http://127.0.0.1:5000/api/users"
payload = {"email": "o5mrsfw0@nittybiz.com", "password": "9057bc90227bb3025b8e2a4049763407678525e5165192e463c27871af3f2893"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response Text:", response.text)