"""
API Test Agent GUI - 测试执行路由

集成执行服务和 WebSocket 推送
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
import asyncio
import json
import logging

from ..services import execution_service
from ..websocket.manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{test_id}/run")
async def run_test(test_id: str, env_id: Optional[str] = None):
    """执行单个测试用例"""
    async def on_progress(data: Dict[str, Any]):
        """进度回调"""
        # 发送进度更新
        await manager.send_progress(
            data["execution_id"],
            data.get("progress", 0),
            data.get("current_step", 0),
            data.get("total_steps", 0),
        )
        
        # 发送日志
        for log in data.get("logs", []):
            await manager.send_log(data["execution_id"], log)
        
        # 发送结果
        if data.get("result"):
            await manager.send_result(data["execution_id"], data["result"])
        
        # 发送状态
        await manager.send_status(data["execution_id"], data["status"], data.get("error"))
    
    try:
        result = await execution_service.run_test(test_id, env_id, on_progress=on_progress)
        return {
            "execution_id": result["execution_id"],
            "message": "测试执行完成",
            "status": result["status"],
            "ws_url": f"/ws/execution/{result['execution_id']}",
        }
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试执行失败: {str(e)}")


@router.post("/batch/run")
async def run_tests_batch(test_ids: list[str], env_id: Optional[str] = None):
    """批量执行测试用例"""
    try:
        result = await execution_service.run_tests_batch(test_ids, env_id)
        return {
            "message": "批量执行完成",
            "total": result["total"],
            "passed": result["passed"],
            "failed": result["failed"],
        }
    except Exception as e:
        logger.error(f"批量执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量执行失败: {str(e)}")


@router.get("/{execution_id}/status")
async def get_execution_status(execution_id: str):
    """获取执行状态"""
    record = execution_service.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return record.to_dict()


@router.get("/history")
async def get_execution_history():
    """获取执行历史"""
    return execution_service.list_executions()


@router.post("/{execution_id}/stop")
async def stop_execution(execution_id: str):
    """停止执行"""
    success = execution_service.stop_execution(execution_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法停止执行（可能已完成或不存在）")
    
    # 通知客户端
    await manager.send_status(execution_id, "stopped")
    
    return {"message": "执行已停止"}


@router.websocket("/ws/execution/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """WebSocket 端点 - 实时推送执行进度"""
    await manager.connect(websocket, execution_id)
    
    try:
        while True:
            # 保持连接，接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "stop":
                # 停止执行
                success = execution_service.stop_execution(execution_id)
                if success:
                    await manager.send_status(execution_id, "stop_requested")
            
            elif message.get("type") == "ping":
                # 心跳
                await manager.send_personal_message({"type": "pong"}, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, execution_id)
    except Exception as e:
        logger.error(f"WebSocket 错误: {str(e)}")
        manager.disconnect(websocket, execution_id)
