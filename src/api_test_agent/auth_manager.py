"""
API Test Agent v2.0 - 认证管理模块

支持多种认证方式：
- OAuth 2.0 (Client Credentials, Password, Authorization Code)
- JWT (自动刷新、签名验证)
- API Key (请求签名、HMAC)
- Basic Auth
- Bearer Token
"""
import time
import hmac
import hashlib
import base64
import logging
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import jwt
import requests

from .client import APIClient


@dataclass
class TokenInfo:
    """Token 信息"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    obtained_at: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        """检查 token 是否已过期"""
        if self.obtained_at == 0:
            return True
        elapsed = time.time() - self.obtained_at
        return elapsed >= (self.expires_in - 60)  # 提前 60 秒刷新
    
    @property
    def expires_at(self) -> datetime:
        """获取过期时间"""
        return datetime.fromtimestamp(self.obtained_at + self.expires_in)


class AuthManager:
    """认证管理器 - 统一管理各种认证方式"""
    
    def __init__(self):
        self.logger = logging.getLogger("AuthManager")
        self.tokens: Dict[str, TokenInfo] = {}
        self.token_refresh_callbacks: Dict[str, Callable] = {}
    
    def register_token(self, name: str, token_info: TokenInfo, 
                      refresh_callback: Callable = None):
        """
        注册一个 token
        
        Args:
            name: token 名称
            token_info: token 信息
            refresh_callback: 刷新回调函数（当 token 过期时调用）
        """
        self.tokens[name] = token_info
        if refresh_callback:
            self.token_refresh_callbacks[name] = refresh_callback
        self.logger.info(f"已注册 token: {name} (过期时间: {token_info.expires_at})")
    
    def get_token(self, name: str) -> Optional[str]:
        """
        获取 token 值（自动刷新如果过期）
        
        Args:
            name: token 名称
        
        Returns:
            token 值
        """
        token_info = self.tokens.get(name)
        if not token_info:
            return None
        
        if token_info.is_expired:
            self.logger.info(f"Token '{name}' 已过期，尝试刷新")
            if name in self.token_refresh_callbacks:
                new_token = self.token_refresh_callbacks[name]()
                self.tokens[name] = new_token
            else:
                self.logger.warning(f"Token '{name}' 没有配置刷新回调")
        
        return self.tokens[name].access_token
    
    def get_auth_headers(self, name: str) -> Dict[str, str]:
        """
        获取认证请求头
        
        Args:
            name: token 名称
        
        Returns:
            认证请求头字典
        """
        token = self.get_token(name)
        if not token:
            return {}
        
        token_info = self.tokens[name]
        return {
            "Authorization": f"{token_info.token_type} {token}"
        }
    
    def apply_auth(self, request_kwargs: Dict, auth_config: Dict):
        """
        将认证应用到请求参数
        
        Args:
            request_kwargs: 请求参数字典
            auth_config: 认证配置
        """
        auth_type = auth_config.get("type", "").lower()
        
        if auth_type == "oauth2":
            self._apply_oauth2(request_kwargs, auth_config)
        elif auth_type == "jwt":
            self._apply_jwt(request_kwargs, auth_config)
        elif auth_type == "api_key":
            self._apply_api_key(request_kwargs, auth_config)
        elif auth_type == "bearer":
            self._apply_bearer(request_kwargs, auth_config)
        elif auth_type == "basic":
            self._apply_basic_auth(request_kwargs, auth_config)
        elif auth_type == "hmac":
            self._apply_hmac(request_kwargs, auth_config)
    
    def _apply_oauth2(self, request_kwargs: Dict, auth_config: Dict):
        """应用 OAuth 2.0 认证"""
        token_name = auth_config.get("token_name", "oauth2")
        token = self.get_token(token_name)
        
        if token:
            request_kwargs.setdefault("headers", {})
            request_kwargs["headers"]["Authorization"] = f"Bearer {token}"
        else:
            self.logger.warning(f"OAuth2 token '{token_name}' 不可用")
    
    def _apply_jwt(self, request_kwargs: Dict, auth_config: Dict):
        """应用 JWT 认证"""
        token_name = auth_config.get("token_name", "jwt")
        token = self.get_token(token_name)
        
        if token:
            request_kwargs.setdefault("headers", {})
            request_kwargs["headers"]["Authorization"] = f"Bearer {token}"
        else:
            self.logger.warning(f"JWT token '{token_name}' 不可用")
    
    def _apply_api_key(self, request_kwargs: Dict, auth_config: Dict):
        """应用 API Key 认证"""
        api_key = auth_config.get("api_key", "")
        key_name = auth_config.get("key_name", "X-API-Key")
        key_location = auth_config.get("key_location", "header")
        
        if key_location == "header":
            request_kwargs.setdefault("headers", {})
            request_kwargs["headers"][key_name] = api_key
        elif key_location == "query":
            request_kwargs.setdefault("params", {})
            request_kwargs["params"][key_name] = api_key
        elif key_location == "cookie":
            request_kwargs.setdefault("cookies", {})
            request_kwargs["cookies"][key_name] = api_key
    
    def _apply_bearer(self, request_kwargs: Dict, auth_config: Dict):
        """应用 Bearer Token 认证"""
        token = auth_config.get("token", "")
        if token:
            request_kwargs.setdefault("headers", {})
            request_kwargs["headers"]["Authorization"] = f"Bearer {token}"
    
    def _apply_basic_auth(self, request_kwargs: Dict, auth_config: Dict):
        """应用 Basic Auth"""
        username = auth_config.get("username", "")
        password = auth_config.get("password", "")
        
        if username and password:
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            request_kwargs.setdefault("headers", {})
            request_kwargs["headers"]["Authorization"] = f"Basic {encoded}"
    
    def _apply_hmac(self, request_kwargs: Dict, auth_config: Dict):
        """应用 HMAC 签名认证"""
        secret_key = auth_config.get("secret_key", "")
        timestamp = str(int(time.time()))
        
        method = request_kwargs.get("method", "GET").upper()
        endpoint = request_kwargs.get("endpoint", "")
        
        # 构建签名字符串
        string_to_sign = f"{method}\n{endpoint}\n{timestamp}"
        
        # 计算 HMAC 签名
        signature = hmac.new(
            secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        request_kwargs.setdefault("headers", {})
        request_kwargs["headers"]["X-HMAC-Signature"] = signature
        request_kwargs["headers"]["X-HMAC-Timestamp"] = timestamp
        request_kwargs["headers"]["X-HMAC-Access-Key"] = auth_config.get("access_key", "")


class OAuth2Client:
    """OAuth 2.0 客户端"""
    
    @staticmethod
    def client_credentials_flow(
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str = None,
        auth_manager: AuthManager = None,
        token_name: str = "oauth2"
    ) -> TokenInfo:
        """
        Client Credentials 流程获取 token
        
        Args:
            token_url: token 端点 URL
            client_id: 客户端 ID
            client_secret: 客户端密钥
            scope: 权限范围
            auth_manager: 认证管理器（可选）
            token_name: token 名称
        
        Returns:
            TokenInfo token 信息
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        if scope:
            data["scope"] = scope
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        token_info = TokenInfo(
            access_token=token_data.get("access_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            scope=token_data.get("scope"),
            obtained_at=time.time()
        )
        
        if auth_manager:
            auth_manager.register_token(token_name, token_info)
        
        return token_info
    
    @staticmethod
    def password_flow(
        token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        scope: str = None,
        auth_manager: AuthManager = None,
        token_name: str = "oauth2"
    ) -> TokenInfo:
        """
        Resource Owner Password 流程获取 token
        
        Args:
            token_url: token 端点 URL
            client_id: 客户端 ID
            client_secret: 客户端密钥
            username: 用户名
            password: 密码
            scope: 权限范围
            auth_manager: 认证管理器
            token_name: token 名称
        
        Returns:
            TokenInfo token 信息
        """
        data = {
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password
        }
        
        if scope:
            data["scope"] = scope
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        token_info = TokenInfo(
            access_token=token_data.get("access_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            obtained_at=time.time()
        )
        
        if auth_manager:
            auth_manager.register_token(token_name, token_info)
        
        return token_info
    
    @staticmethod
    def refresh_token_flow(
        token_url: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        scope: str = None,
        auth_manager: AuthManager = None,
        token_name: str = "oauth2"
    ) -> TokenInfo:
        """
        使用 refresh_token 刷新 access_token
        
        Args:
            token_url: token 端点 URL
            client_id: 客户端 ID
            client_secret: 客户端密钥
            refresh_token: 刷新令牌
            scope: 权限范围
            auth_manager: 认证管理器
            token_name: token 名称
        
        Returns:
            TokenInfo 新的 token 信息
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
        }
        
        if scope:
            data["scope"] = scope
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        token_info = TokenInfo(
            access_token=token_data.get("access_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token", refresh_token),
            scope=token_data.get("scope"),
            obtained_at=time.time()
        )
        
        if auth_manager:
            auth_manager.register_token(token_name, token_info)
        
        return token_info


class JWTManager:
    """JWT 管理器"""
    
    @staticmethod
    def create_jwt(
        payload: Dict,
        secret_key: str,
        algorithm: str = "HS256",
        expires_in: int = 3600,
        issuer: str = None,
        audience: str = None
    ) -> str:
        """
        创建 JWT token
        
        Args:
            payload: JWT 载荷
            secret_key: 密钥
            algorithm: 签名算法
            expires_in: 过期时间（秒）
            issuer: 签发者
            audience: 受众
        
        Returns:
            JWT token 字符串
        """
        now = datetime.utcnow()
        
        claims = payload.copy()
        claims["iat"] = now
        claims["exp"] = now + timedelta(seconds=expires_in)
        
        if issuer:
            claims["iss"] = issuer
        if audience:
            claims["aud"] = audience
        
        token = jwt.encode(claims, secret_key, algorithm=algorithm)
        return token
    
    @staticmethod
    def decode_jwt(token: str, secret_key: str, algorithm: str = "HS256") -> Dict:
        """
        解码 JWT token
        
        Args:
            token: JWT token
            secret_key: 密钥
            algorithm: 签名算法
        
        Returns:
            解码后的载荷
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("JWT token 已过期")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"JWT token 无效: {str(e)}")
    
    @staticmethod
    def is_expired(token: str) -> bool:
        """
        检查 JWT token 是否已过期（无需密钥）
        
        Args:
            token: JWT token
        
        Returns:
            是否已过期
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if exp:
                return time.time() >= exp
            return False
        except Exception:
            return True
    
    @staticmethod
    def extract_payload(token: str) -> Dict:
        """
        提取 JWT token 载荷（不验证签名）
        
        Args:
            token: JWT token
        
        Returns:
            载荷字典
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("无效的 JWT token 格式")
        
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64).decode()
        
        import json
        return json.loads(payload_json)
