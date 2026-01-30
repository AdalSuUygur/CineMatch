import requests
import json

url = "http://localhost:5000/recommend"

# 1. TEST: GUEST (Tür Seçimi)
print("\n--- 🔍 MİSAFİR TESTİ (Aksiyon, Macera, Animasyon) ---")
guest_data = {"selected_genres": [1, 2, 16]}
response = requests.post(url, json=guest_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. TEST: LOGIN (User ID: 1)
print("\n--- 🔥 LOGIN TESTİ (User ID: 1) ---")
user_data = {"user_id": 1}
response = requests.post(url, json=user_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))