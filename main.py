import requests

login_url = "https://www.cbit.ac.in/"

session = requests.Session()

payload = {
    "email": "test1@mail.com",
    "password": "test#1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; Python Login Bot/1.0)"
}

# Attempt login
response = session.post(login_url, data=payload, headers=headers)
print(response)

# Check if login was successful
if "Welcome" in response.text:
    print("Login successful!")
    dashboard_url = "https://bytecorner.vercel.app"
    dashboard_response = session.get(dashboard_url)
    print(dashboard_response.text)
else:
    print("Login failed.")
