from typing import List

from fastapi import WebSocket


class WebSocketManager:
    """
    Manages active WebSocket connections.

    Connections are grouped by organization so that
    one organization's operational events are never
    broadcast to another organization.
    """

    def __init__(self):
        self.connections: dict[int, List[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        organization_id: int,
    ):
        await websocket.accept()

        if organization_id not in self.connections:
            self.connections[organization_id] = []

        self.connections[organization_id].append(
            websocket
        )

    def disconnect(
        self,
        websocket: WebSocket,
        organization_id: int,
    ):
        connections = self.connections.get(
            organization_id,
            [],
        )

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            self.connections.pop(
                organization_id,
                None,
            )

    async def send_personal_message(
        self,
        message: dict,
        websocket: WebSocket,
    ):
        await websocket.send_json(message)

    async def broadcast(
        self,
        message: dict,
        organization_id: int,
    ):
        connections = self.connections.get(
            organization_id,
            [],
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(
                    message
                )
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                websocket,
                organization_id,
            )

    def connection_count(
        self,
        organization_id: int,
    ) -> int:
        return len(
            self.connections.get(
                organization_id,
                [],
            )
        )


websocket_manager = WebSocketManager()