"""
OAuth 2.0 Token 端点
处理授权码换取访问令牌
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import logging

from ...models import OAuthClient, AuthorizationCode, OAuthAccessToken

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_token(request):
    """
    OAuth Token 端点
    
    POST /api/oauth/token
    
    支持两种模式：
    1. authorization_code: 用授权码换取访问令牌
    2. refresh_token: 用刷新令牌获取新的访问令牌
    """
    grant_type = request.data.get('grant_type')
    
    if not grant_type:
        return Response({
            'error': 'invalid_request',
            'error_description': '缺少 grant_type 参数'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if grant_type == 'authorization_code':
        return handle_authorization_code_grant(request)
    elif grant_type == 'refresh_token':
        return handle_refresh_token_grant(request)
    else:
        return Response({
            'error': 'unsupported_grant_type',
            'error_description': f'不支持的 grant_type: {grant_type}'
        }, status=status.HTTP_400_BAD_REQUEST)


def handle_authorization_code_grant(request):
    """处理授权码模式"""
    
    # 获取参数
    code = request.data.get('code')
    client_id = request.data.get('client_id')
    client_secret = request.data.get('client_secret')
    redirect_uri = request.data.get('redirect_uri')
    
    # 参数验证
    if not all([code, client_id, client_secret, redirect_uri]):
        logger.warning(f"[OAuth Token] Missing required parameters")
        return Response({
            'error': 'invalid_request',
            'error_description': '缺少必需参数: code, client_id, client_secret, redirect_uri'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证客户端
    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        logger.warning(f"[OAuth Token] Invalid client_id: {client_id}")
        return Response({
            'error': 'invalid_client',
            'error_description': 'client_id 无效'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 验证客户端密钥
    if not client.verify_secret(client_secret):
        logger.warning(f"[OAuth Token] Invalid client_secret for client: {client.client_name}")
        return Response({
            'error': 'invalid_client',
            'error_description': 'client_secret 错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 验证授权码
    try:
        auth_code = AuthorizationCode.objects.get(code=code, client=client)
    except AuthorizationCode.DoesNotExist:
        logger.warning(f"[OAuth Token] Invalid authorization code")
        return Response({
            'error': 'invalid_grant',
            'error_description': '授权码无效'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查授权码是否有效
    if not auth_code.is_valid():
        error_msg = '授权码已使用' if auth_code.used else '授权码已过期'
        logger.warning(f"[OAuth Token] Authorization code invalid: {error_msg}")
        return Response({
            'error': 'invalid_grant',
            'error_description': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证 redirect_uri 是否匹配
    if auth_code.redirect_uri != redirect_uri:
        logger.warning(f"[OAuth Token] redirect_uri mismatch")
        return Response({
            'error': 'invalid_grant',
            'error_description': 'redirect_uri 不匹配'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 标记授权码为已使用
    auth_code.mark_as_used()
    
    # 生成访问令牌（使用 JWT）
    user = auth_code.user
    refresh = RefreshToken.for_user(user)
    
    # 在 JWT 中添加自定义声明
    refresh['client_id'] = client.client_id
    refresh['scope'] = auth_code.scope
    
    access_token_str = str(refresh.access_token)
    refresh_token_str = str(refresh)
    
    # 保存到数据库
    expires_in = 7200  # 2小时
    access_token_obj = OAuthAccessToken.create_token(
        client=client,
        user=user,
        scope=auth_code.scope,
        token_string=access_token_str,
        refresh_token_string=refresh_token_str,
        expires_in=expires_in
    )
    
    logger.info(f"[OAuth Token] Access token issued for user {user.id}, client {client.client_name}")
    
    # 返回令牌
    return Response({
        'access_token': access_token_str,
        'token_type': 'Bearer',
        'expires_in': expires_in,
        'refresh_token': refresh_token_str,
        'scope': auth_code.scope
    }, status=status.HTTP_200_OK)


def handle_refresh_token_grant(request):
    """处理刷新令牌模式"""
    
    # 获取参数
    refresh_token_str = request.data.get('refresh_token')
    client_id = request.data.get('client_id')
    client_secret = request.data.get('client_secret')
    
    # 参数验证
    if not all([refresh_token_str, client_id, client_secret]):
        logger.warning(f"[OAuth Token] Missing required parameters for refresh")
        return Response({
            'error': 'invalid_request',
            'error_description': '缺少必需参数: refresh_token, client_id, client_secret'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证客户端
    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        logger.warning(f"[OAuth Token] Invalid client_id for refresh: {client_id}")
        return Response({
            'error': 'invalid_client',
            'error_description': 'client_id 无效'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 验证客户端密钥
    if not client.verify_secret(client_secret):
        logger.warning(f"[OAuth Token] Invalid client_secret for refresh")
        return Response({
            'error': 'invalid_client',
            'error_description': 'client_secret 错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 查找原访问令牌
    try:
        old_token = OAuthAccessToken.objects.get(
            refresh_token=refresh_token_str,
            client=client,
            is_revoked=False
        )
    except OAuthAccessToken.DoesNotExist:
        logger.warning(f"[OAuth Token] Invalid refresh_token")
        return Response({
            'error': 'invalid_grant',
            'error_description': 'refresh_token 无效或已撤销'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 生成新的访问令牌
    user = old_token.user
    scope = old_token.scope
    
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    refresh['client_id'] = client.client_id
    refresh['scope'] = scope
    
    new_access_token_str = str(refresh.access_token)
    new_refresh_token_str = str(refresh)
    
    # 撤销旧令牌
    old_token.revoke()
    
    # 创建新令牌
    expires_in = 7200  # 2小时
    new_token = OAuthAccessToken.create_token(
        client=client,
        user=user,
        scope=scope,
        token_string=new_access_token_str,
        refresh_token_string=new_refresh_token_str,
        expires_in=expires_in
    )
    
    logger.info(f"[OAuth Token] Token refreshed for user {user.id}, client {client.client_name}")
    
    # 返回新令牌
    return Response({
        'access_token': new_access_token_str,
        'token_type': 'Bearer',
        'expires_in': expires_in,
        'refresh_token': new_refresh_token_str,
        'scope': scope
    }, status=status.HTTP_200_OK)

