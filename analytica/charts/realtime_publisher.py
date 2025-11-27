import redis
import json

r = redis.Redis(host="redis", port=6379)

def publish_realtime(table, x, y):
    payload = {
        "table": table,
        "x": x,
        "y": y
    }
    r.publish("realtime_channel", json.dumps(payload))
