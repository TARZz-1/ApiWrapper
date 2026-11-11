import requests

response = requests.get("https://api.groq.com/openai/v1/chat/completions")

obj_list = response.json()

