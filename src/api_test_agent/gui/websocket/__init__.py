"""
API Test Agent GUI - WebSocket 处理模块
"""
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, connection_id: str, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
    
    def disconnect(self, connection_id: str):
        """断开连接"""
        self.active_connections.pop(connection_id, None)
    
    async def send_json(self, connection_id: str, data: dict):
        """发送 JSON 消息"""
        ws = self.active_connections.get(connection_id)
        if ws:
            await ws.send_json(data)
    
    async def broadcast(self, data: dict):
        """广播消息"""
        disconnected = []
        for connection_id, ws in self.active_connections.items():
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            self.disconnect(connection_id)


# 全局连接管理器实例
manager = ConnectionManager()
