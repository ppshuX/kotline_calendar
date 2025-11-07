"""
Authentication API - 用户认证管理
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.conf import settings
import requests
import logging

from ..models import AcWingUser
from ..serializers import UserRegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': '注册成功',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前登录用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def acwing_login(request):
    """AcWing OAuth2 一键登录"""
    import traceback
    
    code = request.data.get('code')
    logger.error(f"[AcWing Login] Received code: {code}")
    
    if not code:
        return Response({'error': '缺少授权码'}, status=status.HTTP_400_BAD_REQUEST)
    
    # AcWing 应用信息（从配置文件读取）
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    logger.error(f"[AcWing Login] AppID: {ACWING_APPID}, Secret: {'*' * len(ACWING_SECRET)}")
    
    try:
        # 第二步：申请 access_token 和 openid
        token_url = f"https://www.acwing.com/third_party/api/oauth2/access_token/?appid={ACWING_APPID}&secret={ACWING_SECRET}&code={code}"
        logger.error(f"[AcWing Login] Requesting token URL")
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        logger.error(f"[AcWing Login] Token response: {token_data}")
        
        if 'errcode' in token_data:
            error_msg = f"Failed to get token: {token_data.get('errmsg', 'unknown error')}"
            logger.error(f"[AcWing Login Error] {error_msg}")
            return Response({
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        refresh_token = token_data.get('refresh_token', '')
        logger.error(f"[AcWing Login] Got OpenID: {openid}")
        
        # 第三步：获取用户信息
        userinfo_url = f"https://www.acwing.com/third_party/api/meta/identity/getinfo/?access_token={access_token}&openid={openid}"
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if 'errcode' in userinfo_data:
            return Response({
                'error': f"获取用户信息失败: {userinfo_data.get('errmsg', 'unknown error')}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = userinfo_data['username']
        photo_url = userinfo_data.get('photo', '')
        
        # 查找或创建用户
        acwing_user = AcWingUser.objects.filter(openid=openid).first()
        
        if acwing_user:
            # 已存在的用户，更新token
            acwing_user.access_token = access_token
            acwing_user.refresh_token = refresh_token
            acwing_user.photo_url = photo_url
            acwing_user.save()
            user = acwing_user.user
            # 更新用户名（如果AcWing上修改了）
            if user.username != username:
                # 检查新用户名是否已被其他用户占用
                if not User.objects.filter(username=username).exclude(id=user.id).exists():
                    user.username = username
                    user.save()
        else:
            # 新用户，创建账号
            # 检查用户名是否已存在，如果存在则添加后缀
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                password=None  # AcWing登录不需要密码
            )
            
            AcWingUser.objects.create(
                user=user,
                openid=openid,
                access_token=access_token,
                refresh_token=refresh_token,
                photo_url=photo_url
            )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'photo': photo_url
            }
        }, status=status.HTTP_200_OK)
        
    except requests.RequestException as e:
        error_msg = f'Request AcWing API failed: {str(e)}'
        logger.error(f"[AcWing Login Error] {error_msg}")
        logger.error(traceback.format_exc())
        return Response({
            'error': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        error_msg = f'Login failed: {str(e)}'
        logger.error(f"[AcWing Login Error] {error_msg}")
        logger.error(traceback.format_exc())
        return Response({
            'error': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

