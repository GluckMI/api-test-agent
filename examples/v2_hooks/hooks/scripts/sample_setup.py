"""
API Test Agent v2.0 - 示例脚本钩子

这是一个示例 Python 脚本，用于演示 Script 类型钩子的用法。
脚本钩子接收 context 参数（包含之前钩子提取的所有变量），
返回一个字典（其中的键值对会被提取到上下文中）。

使用方法：
  在 YAML 中引用此脚本：
    setup:
      - name: "执行自定义脚本"
        type: script
        script: "examples/v2_hooks/hooks/scripts/sample_setup.py"
        extract:
          custom_var: "my_custom_value"
          timestamp: "generated_time"

函数签名要求：
  def execute(context: dict) -> dict:
      '''
      Args:
          context: 包含所有已提取变量的字典
                  例如: {"user_id": 123, "token": "abc..."}
      
      Returns:
          dict: 要提取到上下文中的新变量
                例如: {"custom_var": "value", "timestamp": "2026-01-01"}
      '''

注意：
  1. 函数名必须是 execute
  2. 必须接受 context 参数
  3. 返回值必须是字典或 None
  4. 如果抛出异常，钩子会被标记为失败
"""

import time
import random
import string
from datetime import datetime
from typing import Dict, Any


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行自定义初始化逻辑
    
    本示例演示以下功能：
    1. 读取 context 中已有的变量
    2. 生成新的变量（时间戳、随机字符串等）
    3. 返回复杂的数据结构
    """
    
    print(f"[Script Hook] 开始执行...")
    print(f"[Script Hook] 收到的上下文变量: {list(context.keys())}")
    
    # ----------------------------------------------------------
    # 示例 1：生成时间戳
    # ----------------------------------------------------------
    generated_time = datetime.now().isoformat()
    print(f"[Script Hook] 生成时间戳: {generated_time}")
    
    # ----------------------------------------------------------
    # 示例 2：生成随机字符串（可用于创建唯一测试数据）
    # ----------------------------------------------------------
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    unique_test_name = f"auto_test_{random_suffix}"
    print(f"[Script Hook] 生成唯一名称: {unique_test_name}")
    
    # ----------------------------------------------------------
    # 示例 3：读取并处理 context 中的变量
    # ----------------------------------------------------------
    if 'admin_user_id' in context:
        user_id = context['admin_user_id']
        print(f"[Script Hook] 检测到管理员用户 ID: {user_id}")
        
        # 可以基于已有变量生成派生变量
        derived_user_email = f"test_{user_id}@example.com"
    else:
        derived_user_email = "default_test@example.com"
        print("[Script Hook] 未找到 admin_user_id，使用默认邮箱")
    
    # ----------------------------------------------------------
    # 示例 4：模拟耗时操作（如数据库查询、外部 API 调用）
    # ----------------------------------------------------------
    print("[Script Hook] 执行初始化操作...")
    time.sleep(0.1)  # 模拟短暂延迟
    
    fixture_status = {
        "loaded": True,
        "count": 10,
        "loaded_at": generated_time,
        "source": "sample_setup.py"
    }
    print(f"[Script Hook] Fixtures 加载完成: {fixture_status}")
    
    # ----------------------------------------------------------
    # 返回要提取到上下文中的变量
    # ----------------------------------------------------------
    result = {
        # 简单值
        "my_custom_value": "generated_by_script",
        "generated_time": generated_time,
        "unique_test_name": unique_test_name,
        "derived_user_email": derived_user_email,
        
        # 复杂值（字典会被序列化存储）
        "fixture_status": str(fixture_status),
        
        # 计数器
        "script_execution_count": 1,
    }
    
    print(f"[Script Hook] 返回 {len(result)} 个变量")
    print(f"[Script Hook] 执行完成")
    
    return result


if __name__ == "__main__":
    # 支持直接运行进行测试
    print("=" * 60)
    print("Script Hook 测试模式")
    print("=" * 60)
    
    test_context = {
        "admin_user_id": 42,
        "admin_token": "test_token_123",
        "debug_mode": True,
    }
    
    result = execute(test_context)
    
    print("\n返回的结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")
