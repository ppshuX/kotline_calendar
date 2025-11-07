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

from ..models import AcWingUser, QQUser
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
    
    if not code:
        return Response({'error': '缺少授权码'}, status=status.HTTP_400_BAD_REQUEST)
    
    # AcWing 应用信息（从配置文件读取）
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    
    try:
        # 第二步：申请 access_token 和 openid
        token_url = f"https://www.acwing.com/third_party/api/oauth2/access_token/?appid={ACWING_APPID}&secret={ACWING_SECRET}&code={code}"
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            error_msg = f"Failed to get token: {token_data.get('errmsg', 'unknown error')}"
            logger.error(f"[AcWing Login] {error_msg}")
            return Response({
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        refresh_token = token_data.get('refresh_token', '')
        
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


@api_view(['POST'])
@permission_classes([AllowAny])
def qq_login(request):
    """QQ OAuth2 一键登录"""
    import traceback
    
    code = request.data.get('code')
    
    if not code:
        return Response({'error': '缺少授权码'}, status=status.HTTP_400_BAD_REQUEST)
    
    # QQ 应用信息（从配置文件读取）
    QQ_APPID = getattr(settings, 'QQ_APPID', '')
    QQ_APPKEY = getattr(settings, 'QQ_APPKEY', '')
    QQ_REDIRECT_URI = 'https://app7626.acapp.acwing.com.cn/qq/callback'
    
    try:
        # 第一步：通过 code 获取 access_token
        token_url = "https://graph.qq.com/oauth2.0/token"
        token_params = {
            'grant_type': 'authorization_code',
            'client_id': QQ_APPID,
            'client_secret': QQ_APPKEY,
            'code': code,
            'redirect_uri': QQ_REDIRECT_URI
        }
        token_response = requests.get(token_url, params=token_params, timeout=10)
        
        # QQ 返回的是 URL 参数格式，需要解析
        token_text = token_response.text
        if 'access_token' not in token_text:
            return Response({
                'error': f'获取token失败: {token_text}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析 access_token
        import urllib.parse
        token_dict = urllib.parse.parse_qs(token_text)
        access_token = token_dict['access_token'][0]
        refresh_token = token_dict.get('refresh_token', [''])[0]
        
        # 第二步：获取 OpenID
        openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}"
        openid_response = requests.get(openid_url, timeout=10)
        openid_text = openid_response.text
        
        # 解析 OpenID（返回格式：callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );）
        import json
        import re
        match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
        if not match:
            return Response({
                'error': '获取OpenID失败'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        openid_data = json.loads(match.group(1))
        openid = openid_data['openid']
        
        # 第三步：获取用户信息
        userinfo_url = "https://graph.qq.com/user/get_user_info"
        userinfo_params = {
            'access_token': access_token,
            'oauth_consumer_key': QQ_APPID,
            'openid': openid
        }
        userinfo_response = requests.get(userinfo_url, params=userinfo_params, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if userinfo_data.get('ret') != 0:
            return Response({
                'error': f"获取用户信息失败: {userinfo_data.get('msg', 'unknown error')}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        nickname = userinfo_data.get('nickname', 'QQ用户')
        photo_url = userinfo_data.get('figureurl_qq_2') or userinfo_data.get('figureurl_qq_1', '')
        
        # 查找或创建用户
        qq_user = QQUser.objects.filter(openid=openid).first()
        
        if qq_user:
            # 已存在的用户，更新token和信息
            qq_user.access_token = access_token
            qq_user.refresh_token = refresh_token
            qq_user.photo_url = photo_url
            qq_user.nickname = nickname
            qq_user.save()
            user = qq_user.user
        else:
            # 新用户，创建账号
            # 使用 QQ 昵称作为用户名，如果冲突则添加后缀
            username = nickname
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                password=None  # QQ登录不需要密码
            )
            
            QQUser.objects.create(
                user=user,
                openid=openid,
                access_token=access_token,
                refresh_token=refresh_token,
                photo_url=photo_url,
                nickname=nickname
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
        error_msg = f'Request QQ API failed: {str(e)}'
        logger.error(f"[QQ Login Error] {error_msg}")
        logger.error(traceback.format_exc())
        return Response({
            'error': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        error_msg = f'Login failed: {str(e)}'
        logger.error(f"[QQ Login Error] {error_msg}")
        logger.error(traceback.format_exc())
        return Response({
            'error': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_acwing_login_url(request):
    """获取 AcWing 登录授权 URL"""
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    REDIRECT_URI = 'https://app7626.acapp.acwing.com.cn/oauth2/receive_code/'
    
    # 构建授权 URL
    apply_code_url = f"https://www.acwing.com/third_party/api/oauth2/web/authorize/?appid={ACWING_APPID}&redirect_uri={REDIRECT_URI}&scope=userinfo&state=acwing"
    
    return Response({
        'apply_code_url': apply_code_url
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qq_login_url(request):
    """获取 QQ 登录授权 URL"""
    QQ_APPID = getattr(settings, 'QQ_APPID', '')
    REDIRECT_URI = 'https://app7626.acapp.acwing.com.cn/qq/callback'
    
    # 构建授权 URL
    apply_code_url = f"https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id={QQ_APPID}&redirect_uri={REDIRECT_URI}&state=qq"
    
    return Response({
        'apply_code_url': apply_code_url
    })

