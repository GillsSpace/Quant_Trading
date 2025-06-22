from polygon import RESTClient
import json

with open("keys.json") as f:
    keys = json.load(f)

KEY = keys["polygon_key"]

client = RESTClient(KEY)

grouped = client.get_grouped_daily_aggs(
    "2025-06-02",
    adjusted="true",
)

print(grouped)
