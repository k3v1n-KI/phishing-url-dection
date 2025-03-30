import requests
from feature_extractor import extract_features
from phishing_model import Model

BASE = "http://127.0.0.1:5000/"

response = requests.put(BASE + "model/1", json={"url": "https://pypi.org/project/whois/"})

try:
    print(response.json())
except requests.exceptions.JSONDecodeError:
    print("No JSON response. Here's the raw response text:")
    print(response.text)



# features = extract_features("https://pypi.org/project/whois/")
# print(features)
# print(len(features))

