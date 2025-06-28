import requests

port = 8000
endpoint = f"http://localhost:{port}/api/user/3"

r_get = requests.get(endpoint, params={"query": "123"}, json={"samu": "123"})

print(r_get.json())
print(r_get.status_code)

#User creation

