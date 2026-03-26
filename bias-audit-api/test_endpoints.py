import requests
import json

BASE = "http://127.0.0.1:8000"

def sep(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)

sep("GET /health")
r = requests.get(f"{BASE}/health")
print(json.dumps(r.json(), indent=2))

sep("POST /api/analyse")
payload = {"content": "Young Muslim men are disproportionately represented in knife crime statistics across London boroughs"}
r = requests.post(f"{BASE}/api/analyse", json=payload)
analyse_result = r.json()
print(json.dumps(analyse_result, indent=2))

sep("POST /api/explain")
explain_payload = {
    "score":       analyse_result.get("score",      85.0),
    "category":    analyse_result.get("category",   "racial_bias"),
    "confidence":  analyse_result.get("confidence", 0.85),
    "shap_values": analyse_result.get("shap_values", {"muslim": 0.34, "crime": 0.28}),
}
r = requests.post(f"{BASE}/api/explain", json=explain_payload)
print(json.dumps(r.json(), indent=2))

sep("GET /api/audit")
r = requests.get(f"{BASE}/api/audit")
print(json.dumps(r.json(), indent=2))

sep("GET /api/audit/history")
r = requests.get(f"{BASE}/api/audit/history")
print(json.dumps(r.json(), indent=2))

print("\nALL ENDPOINTS TESTED")
