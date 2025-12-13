# backend/app/websocket_server.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Callable
import asyncio

router = APIRouter()
connections: List[WebSocket] = []

async def broadcast(message: dict):
    disconnected = []
    for ws in connections:
        try:
            await ws.send_json(message)
        except:
            disconnected.append(ws)
    for d in disconnected:
        connections.remove(d)

@router.websocket("/feed")
async def ws_feed(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # Keep alive; optionally accept messages
            msg = await websocket.receive_text()
            # echo for now
            await websocket.send_text(f"ack: {msg}")
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)
