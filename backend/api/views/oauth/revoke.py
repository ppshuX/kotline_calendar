"""
OAuth 2.0 Token 撤销端点
允许用户撤销已授权的访问令牌
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from ...models import OAuthAccessToken, OAuthClient

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def oauth_revoke(request):
    """
    OAuth Token 撤销端点
    
    POST /api/oauth/revoke
    
    撤销指定客户端的所有访问令牌
    或撤销当前使用的访问令牌
    
    请求参数：
    - client_id: 要撤销的客户端ID（可选，如果不提供则撤销当前token）
    - revoke_all: 是否撤销该客户端的所有token（默认false）
    """
    user = request.user
    client_id = request.data.get('client_id')
    revoke_all = request.data.get('revoke_all', False)
    
    # 如果提供了 client_id，撤销该客户端的令牌
    if client_id:
        try:
            client = OAuthClient.objects.get(client_id=client_id)
        except OAuthClient.DoesNotExist:
            return Response({
                'error': 'invalid_client',
                'error_description': 'client_id 无效'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if revoke_all:
            # 撤销该用户对该客户端的所有令牌
            count = OAuthAccessToken.revoke_all_for_client(user, client)
            logger.info(f"[OAuth Revoke] Revoked all tokens ({count}) for user {user.id}, client {client.client_name}")
            return Response({
                'success': True,
                'message': f'已撤销 {count} 个访问令牌',
                'revoked_count': count
            }, status=status.HTTP_200_OK)
        else:
            # 撤销该用户对该客户端的第一个有效令牌
            try:
                token = OAuthAccessToken.objects.filter(
                    user=user,
                    client=client,
                    is_revoked=False
                ).first()
                
                if token:
                    token.revoke()
                    logger.info(f"[OAuth Revoke] Token revoked for user {user.id}, client {client.client_name}")
                    return Response({
                        'success': True,
                        'message': '访问令牌已撤销'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'no_token',
                        'error_description': '未找到有效的访问令牌'
                    }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"[OAuth Revoke] Error: {str(e)}")
                return Response({
                    'error': 'server_error',
                    'error_description': '撤销失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 如果没有提供 client_id，尝试撤销当前请求使用的令牌
    else:
        # 从请求头获取当前 token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token_str = auth_header[7:]  # 去掉 "Bearer " 前缀
            
            try:
                token = OAuthAccessToken.objects.get(
                    token=token_str,
                    user=user,
                    is_revoked=False
                )
                token.revoke()
                logger.info(f"[OAuth Revoke] Current token revoked for user {user.id}")
                return Response({
                    'success': True,
                    'message': '当前访问令牌已撤销'
                }, status=status.HTTP_200_OK)
            except OAuthAccessToken.DoesNotExist:
                return Response({
                    'error': 'no_token',
                    'error_description': '未找到有效的访问令牌'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'error': 'invalid_request',
                'error_description': '缺少 client_id 参数或 Authorization 头'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def oauth_authorized_apps(request):
    """
    获取用户已授权的应用列表
    
    GET /api/oauth/authorized-apps
    """
    user = request.user
    
    # 获取所有有效的访问令牌（按客户端分组）
    tokens = OAuthAccessToken.objects.filter(
        user=user,
        is_revoked=False
    ).select_related('client').order_by('-created_at')
    
    # 按客户端分组
    apps_dict = {}
    for token in tokens:
        client_id = token.client.client_id
        if client_id not in apps_dict:
            apps_dict[client_id] = {
                'client_id': token.client.client_id,
                'client_name': token.client.client_name,
                'client_description': token.client.client_description,
                'logo_url': token.client.logo_url,
                'website_url': token.client.website_url,
                'scope': token.scope,
                'authorized_at': token.created_at.isoformat(),
                'last_used_at': token.last_used_at.isoformat() if token.last_used_at else None,
                'token_count': 1
            }
        else:
            apps_dict[client_id]['token_count'] += 1
    
    apps_list = list(apps_dict.values())
    
    logger.info(f"[OAuth] Returned {len(apps_list)} authorized apps for user {user.id}")
    
    return Response({
        'apps': apps_list,
        'total': len(apps_list)
    }, status=status.HTTP_200_OK)

