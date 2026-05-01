"""
API 接口自动化测试 Agent - API 客户端封装
"""
import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from config import config


@dataclass
class APIResponse:
    """API 响应数据结构"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    response_time: float
    success: bool
    error_message: Optional[str] = None


class APIClient:
    """API 客户端封装类"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.get("base_url", "")
        self.timeout = timeout or config.get("timeout", 30)
        self.retry_times = config.get("retry_times", 3)
        self.retry_delay = config.get("retry_delay", 1)
        self.default_headers = config.get("headers", {"Content-Type": "application/json"})
        self.session = requests.Session()
    
    def _prepare_url(self, endpoint: str) -> str:
        """准备完整的 URL"""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        # 确保 base_url 以 / 结尾，endpoint 不以 / 开头
        base = self.base_url.rstrip('/')
        ep = endpoint.lstrip('/')
        return f"{base}/{ep}" if base else ep
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """合并默认 headers 和自定义 headers"""
        merged = self.default_headers.copy()
        if headers:
            merged.update(headers)
        return merged
    
    def _send_request(self, method: str, url: str, **kwargs) -> APIResponse:
        """发送单个请求"""
        start_time = time.time()
        try:
            # 从 kwargs 中移除 timeout（已在 request 方法中设置）
            kwargs.pop('timeout', None)
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response_time = time.time() - start_time
            
            # 尝试解析 JSON 响应
            try:
                body = response.json()
            except:
                body = response.text
            
            return APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
                response_time=response_time,
                success=True
            )
        except requests.exceptions.Timeout as e:
            return APIResponse(
                status_code=0,
                headers={},
                body=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=f"请求超时：{str(e)}"
            )
        except requests.exceptions.ConnectionError as e:
            return APIResponse(
                status_code=0,
                headers={},
                body=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=f"连接错误：{str(e)}"
            )
        except Exception as e:
            return APIResponse(
                status_code=0,
                headers={},
                body=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def request(self, method: str, endpoint: str, 
                params: Optional[Dict] = None,
                data: Optional[Any] = None,
                json_data: Optional[Any] = None,
                headers: Optional[Dict[str, str]] = None,
                auth: Optional[tuple] = None) -> APIResponse:
        """发送 API 请求（带重试）"""
        url = self._prepare_url(endpoint)
        prepared_headers = self._prepare_headers(headers)
        
        # 构建请求参数
        request_kwargs = {
            'params': params,
            'headers': prepared_headers,
            'timeout': self.timeout
        }
        
        if data:
            request_kwargs['data'] = data
        if json_data:
            request_kwargs['json'] = json_data
        if auth:
            request_kwargs['auth'] = auth
        
        # 执行请求（带重试）
        last_response = None
        for attempt in range(self.retry_times):
            last_response = self._send_request(method, url, **request_kwargs)
            if last_response.success and last_response.status_code < 500:
                break  # 成功或 4xx 错误，不重试
            if attempt < self.retry_times - 1:
                time.sleep(self.retry_delay)
        
        return last_response
    
    def get(self, endpoint: str, **kwargs) -> APIResponse:
        """GET 请求"""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> APIResponse:
        """POST 请求"""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> APIResponse:
        """PUT 请求"""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """DELETE 请求"""
        return self.request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> APIResponse:
        """PATCH 请求"""
        return self.request('PATCH', endpoint, **kwargs)
    
    def close(self):
        """关闭会话"""
        self.session.close()
