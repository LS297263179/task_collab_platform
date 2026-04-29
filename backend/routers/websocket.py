import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
from config import settings

router = APIRouter()

# Connected clients by project_id: {project_id: {websocket_set}}
connections: dict[int, set[WebSocket]] = {}


async def get_redis():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: int):
    await websocket.accept()
    project_id = int(project_id)

    if project_id not in connections:
        connections[project_id] = set()
    connections[project_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all clients in this project
            message = json.loads(data)
            for client in connections.get(project_id, set()):
                if client != websocket:
                    try:
                        await client.send_text(json.dumps(message))
                    except Exception:
                        pass
    except WebSocketDisconnect:
        connections.get(project_id, set()).discard(websocket)
        if not connections.get(project_id):
            connections.pop(project_id, None)
