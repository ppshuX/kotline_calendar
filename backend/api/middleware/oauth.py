"""
OAuth 2.0 权限验证中间件和装饰器
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
import logging

from ..models import OAuthAccessToken

logger = logging.getLogger(__name__)


def require_oauth_scope(*required_scopes):
    """
    OAuth Scope 权限装饰器
    
    用法:
        @api_view(['GET'])
        @require_oauth_scope('calendar:read')
        def my_view(request):
            ...
    
    或要求多个权限:
        @require_oauth_scope('calendar:read', 'calendar:write')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # 检查是否通过 OAuth 认证
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if not auth_header.startswith('Bearer '):
                logger.warning(f"[OAuth Middleware] Missing or invalid Authorization header")
                return Response({
                    'error': 'invalid_token',
                    'error_description': '缺少或无效的 Authorization 头'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            token_str = auth_header[7:]  # 去掉 "Bearer " 前缀
            
            # 验证 JWT token
            try:
                access_token = AccessToken(token_str)
                user_id = access_token['user_id']
            except TokenError as e:
                logger.warning(f"[OAuth Middleware] Invalid JWT token: {str(e)}")
                return Response({
                    'error': 'invalid_token',
                    'error_description': 'Token 无效或已过期'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 查找数据库中的记录
            try:
                oauth_token = OAuthAccessToken.objects.get(
                    token=token_str,
                    is_revoked=False
                )
            except OAuthAccessToken.DoesNotExist:
                logger.warning(f"[OAuth Middleware] Token not found or revoked")
                return Response({
                    'error': 'invalid_token',
                    'error_description': 'Token 已撤销或不存在'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查 token 是否过期
            if not oauth_token.is_valid():
                logger.warning(f"[OAuth Middleware] Token expired")
                return Response({
                    'error': 'invalid_token',
                    'error_description': 'Token 已过期'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查权限范围
            token_scopes = set(oauth_token.scope.split())
            required_scopes_set = set(required_scopes)
            
            if not required_scopes_set.issubset(token_scopes):
                missing_scopes = required_scopes_set - token_scopes
                logger.warning(f"[OAuth Middleware] Insufficient scope. Missing: {missing_scopes}")
                return Response({
                    'error': 'insufficient_scope',
                    'error_description': f'权限不足，缺少: {", ".join(missing_scopes)}'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 更新最后使用时间
            oauth_token.update_last_used()
            
            # 将 OAuth 信息附加到 request 对象
            request.oauth_token = oauth_token
            request.oauth_client = oauth_token.client
            request.oauth_scope = oauth_token.scope
            
            logger.debug(f"[OAuth Middleware] Request authorized for user {user_id}, client {oauth_token.client.client_name}")
            
            # 调用原视图函数
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def get_oauth_user(request):
    """
    从 OAuth token 获取用户对象
    
    用法:
        user = get_oauth_user(request)
        if user:
            # 用户已通过 OAuth 认证
            ...
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token_str = auth_header[7:]
    
    try:
        oauth_token = OAuthAccessToken.objects.get(
            token=token_str,
            is_revoked=False
        )
        if oauth_token.is_valid():
            return oauth_token.user
    except OAuthAccessToken.DoesNotExist:
        pass
    
    return None


def check_oauth_scope(request, required_scope):
    """
    检查请求是否有所需的 OAuth 权限
    
    用法:
        if check_oauth_scope(request, 'calendar:write'):
            # 有权限
            ...
        else:
            # 无权限
            ...
    """
    if not hasattr(request, 'oauth_token'):
        return False
    
    return request.oauth_token.has_scope(required_scope)

