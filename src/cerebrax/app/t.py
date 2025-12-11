import requests

url = "http://127.0.0.1:8000/shutdown/launch"
response = requests.post(url, json={"shutdown": True})
# print(response.json())
