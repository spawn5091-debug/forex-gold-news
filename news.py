import requests

url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

r = requests.get(
    url,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0"}
)

print("STATUS:", r.status_code)
print("TYPE:", r.headers.get("content-type"))
print("EVENTS:", len(r.json()))
