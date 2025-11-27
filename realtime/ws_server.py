import asyncio
import redis
import websockets
import json

r = redis.Redis(host="redis", port=6379)

async def handler(websocket):
    pubsub = r.pubsub()
    pubsub.subscribe("realtime_channel")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"].decode())
            await websocket.send(json.dumps(data))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())
