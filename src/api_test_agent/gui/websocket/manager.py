"""
API Test Agent GUI - WebSocket 连接管理

管理 WebSocket 连接、消息广播和心跳保活
"""
from typing import Dict, Set, Any
from fastapi import WebSocket
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """连接 WebSocket"""
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        self.active_connections[execution_id].add(websocket)
        logger.info(f"WebSocket 连接已建立: execution_id={execution_id}")
    
    def disconnect(self, websocket: WebSocket, execution_id: str):
        """断开 WebSocket 连接"""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
            logger.info(f"WebSocket 连接已断开: execution_id={execution_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)
    
    async def broadcast(self, execution_id: str, message: Dict[str, Any]):
        """广播消息到指定执行 ID 的所有连接"""
        if execution_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[execution_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.active_connections[execution_id].discard(connection)
    
    async def send_progress(self, execution_id: str, progress: float, current_step: int, total_steps: int):
        """发送进度更新"""
        message = {
            "type": "progress",
            "execution_id": execution_id,
            "progress": progress,
            "current_step": current_step,
            "total_steps": total_steps,
        }
        await self.broadcast(execution_id, message)
    
    async def send_result(self, execution_id: str, result: Dict[str, Any]):
        """发送执行结果"""
        message = {
            "type": "result",
            "execution_id": execution_id,
            "result": result,
        }
        await self.broadcast(execution_id, message)
    
    async def send_log(self, execution_id: str, log_message: str, level: str = "info"):
        """发送日志消息"""
        message = {
            "type": "log",
            "execution_id": execution_id,
            "message": log_message,
            "level": level,
        }
        await self.broadcast(execution_id, message)
    
    async def send_status(self, execution_id: str, status: str, error: str = None):
        """发送状态更新"""
        message = {
            "type": "status",
            "execution_id": execution_id,
            "status": status,
        }
        if error:
            message["error"] = error
        await self.broadcast(execution_id, message)
    
    def has_connections(self, execution_id: str) -> bool:
        """检查是否有活动连接"""
        return execution_id in self.active_connections and len(self.active_connections[execution_id]) > 0


# 全局连接管理器实例
manager = ConnectionManager()
