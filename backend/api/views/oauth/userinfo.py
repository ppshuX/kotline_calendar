"""
OAuth 2.0 UserInfo 端点
返回用户基本信息
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def oauth_userinfo(request):
    """
    OAuth UserInfo 端点
    
    GET /api/oauth/userinfo
    
    返回当前认证用户的基本信息
    需要在请求头中携带: Authorization: Bearer {access_token}
    """
    user = request.user
    
    # 获取用户的第三方账号信息
    provider = 'email'
    openid = None
    unionid = None
    
    if hasattr(user, 'qq_profile'):
        provider = 'qq'
        openid = user.qq_profile.openid
        unionid = user.qq_profile.unionid
    elif hasattr(user, 'acwing_profile'):
        provider = 'acwing'
        openid = user.acwing_profile.openid
    
    # 构建响应数据
    user_data = {
        'user_id': user.id,
        'username': user.first_name or user.username,
        'email': user.email if user.email else None,
        'provider': provider,
        'created_at': user.date_joined.isoformat(),
    }
    
    # 添加头像（如果有）
    if hasattr(user, 'qq_profile') and user.qq_profile.photo:
        user_data['avatar'] = user.qq_profile.photo
    elif hasattr(user, 'acwing_profile') and user.acwing_profile.photo:
        user_data['avatar'] = user.acwing_profile.photo
    
    # 添加第三方ID（如果scope包含相关权限）
    # 这里简化处理，直接返回
    if openid:
        user_data['openid'] = openid
    if unionid:
        user_data['unionid'] = unionid
    
    logger.info(f"[OAuth UserInfo] Returned info for user {user.id}")
    
    return Response(user_data, status=status.HTTP_200_OK)

