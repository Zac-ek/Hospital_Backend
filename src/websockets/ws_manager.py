from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from uuid import uuid4
from sqlalchemy.orm import Session
from src.helpers.jwt_config import jwt_config
from src.db.db_mysql import databaseMysql
from src.dao.grupos_sanguineos_dao import grupos_sanguineos_dao
import jwt

class WebSocketManager:
    """
    Clase para manejar conexiones WebSocket con soporte de canales.
    """
    def __init__(self):
        self.clients: Dict[str, WebSocket] = {}
        self.channels: Dict[str, set] = {}

    async def connect(self, websocket: WebSocket, token: str):
        try:
            payload = jwt_config.valida_token(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            await websocket.close(code=1008)
            return None, []

        client_id = str(uuid4())
        self.clients[client_id] = websocket

        roles = payload.get("roles", [])
        for role in roles:
            if role not in self.channels:
                self.channels[role] = set()
            self.channels[role].add(client_id)

        await websocket.accept()
        await websocket.send_json({
            "client_id": client_id,
            "roles_asigned": roles,
            "message": f"Conectado a roles/canales: {roles}"
        })

        return client_id, roles

    async def listen(self, websocket: WebSocket, client_id: str, roles: list):
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"Mensaje recibido: {message}")
        except WebSocketDisconnect:
            self.disconnect(client_id, roles)

    def disconnect(self, client_id: str, roles: list):
        for role in roles:
            if role in self.channels:
                self.channels[role].discard(client_id)
        self.clients.pop(client_id, None)

    async def broadcast(self, data: dict, channels: list[str]):
        """
        Envía un mensaje a todos los clientes pertenecientes a uno o más canales (roles).

        Args:
            data (dict): Datos a enviar.
            channels (list): Lista de nombres de canales (roles).
        """
        # Usamos un set para evitar enviar dos veces a un mismo cliente
        unique_clients = set()
        for channel in channels:
            if channel in self.channels:
                unique_clients.update(self.channels[channel])

        disconnected = []
        for client_id in unique_clients:
            client = self.clients.get(client_id)
            if client:
                try:
                    await client.send_json(data)
                except Exception:
                    disconnected.append(client_id)

        for client_id in disconnected:
            # Se eliminan de todos los canales en los que estén
            self.disconnect(client_id, channels)

    async def send_message_to_client(self, client_id: str, data: dict):
        client = self.clients.get(client_id)
        if client:
            await client.send_json(data)


# Instancia global para usar en otros módulos
ws_manager = WebSocketManager()
