import redis, json
from analytica.etl.etl_engine import run_etl

r = redis.Redis(host="redis", port=6379)

while True:
    messages = r.xread({"analystica_stream": "$"}, block=0)
    for stream, msgs in messages:
        for msg_id, msg_data in msgs:
            event = json.loads(msg_data[b"data"].decode())
            if event["event"] == "UPLOAD_COMPLETED":
                run_etl(event["payload"])
