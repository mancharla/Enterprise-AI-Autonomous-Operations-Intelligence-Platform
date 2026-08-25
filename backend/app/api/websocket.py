from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.services.websocket_manager import websocket_manager


router = APIRouter(
    tags=["WebSocket"],
)


def authenticate_websocket(token: str | None):

    if not token:
        return None

    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")
    organization_id = payload.get("organization_id")

    if not user_id or not organization_id:
        return None

    try:
        return {
            "user_id": int(user_id),
            "organization_id": int(organization_id),
            "role": payload.get("role"),
        }

    except (TypeError, ValueError):
        return None


@router.websocket(
    "/ws/organization/{organization_id}"
)
async def organization_websocket(
    websocket: WebSocket,
    organization_id: int,
):

    token = websocket.query_params.get("token")

    user = authenticate_websocket(token)

    if not user:

        await websocket.close(
            code=1008,
            reason="Invalid or expired authentication token",
        )

        return

    # Security: user can only connect to their own organization
    if user["organization_id"] != organization_id:

        await websocket.close(
            code=1008,
            reason="Organization access denied",
        )

        return

    await websocket_manager.connect(
        websocket=websocket,
        organization_id=organization_id,
    )

    try:

        await websocket.send_json(
            {
                "event": "connection_established",
                "organization_id": organization_id,
                "user_id": user["user_id"],
                "role": user["role"],
                "timestamp": datetime.utcnow().isoformat(),
                "message": (
                    "Real-time organization connection "
                    "established successfully."
                ),
            }
        )

        while True:

            data = await websocket.receive_json()

            await websocket.send_json(
                {
                    "event": "message_received",
                    "organization_id": organization_id,
                    "message": data,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    except WebSocketDisconnect:

        websocket_manager.disconnect(
            websocket=websocket,
            organization_id=organization_id,
        )

    except Exception:

        websocket_manager.disconnect(
            websocket=websocket,
            organization_id=organization_id,
        )