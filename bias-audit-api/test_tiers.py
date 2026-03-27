import requests

BASE = "http://127.0.0.1:8000"

tests = [
    "you racist",
    "why are you so racist",
    "you are a christian",
    "Women are too emotional to be effective managers in high pressure corporate environments",
    "Muslim communities in Birmingham are refusing to integrate and undermining British values",
    "The UK government announced a new fund to improve public transport across rural England",
]

print(f"{'TIER':<6} {'CATEGORY':<25} {'SCORE':<8} CONTENT")
print("-" * 95)

for text in tests:
    r = requests.post(f"{BASE}/api/analyse", json={"content": text})
    d = r.json()
    tier = d.get("tier", "?")
    category = d.get("category", "?")
    score = d.get("score", "?")
    reason = d.get("tier_reason", "")
    print(f"{tier:<6} {category:<25} {str(score):<8} {text[:55]}")
    if reason:
        print(f"       reason: {reason[:85]}")
    print()
