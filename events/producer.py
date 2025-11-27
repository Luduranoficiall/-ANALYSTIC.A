import redis
import json

r = redis.Redis(host="redis", port=6379)

def publish(event_type, payload):
    data = {
        "event": event_type,
        "payload": payload
    }
    r.xadd("analystic_a_stream", {"data": json.dumps(data)})
