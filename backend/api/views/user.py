"""
User Profile API - 用户个人中心
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import Event, AcWingUser, QQUser
from ..serializers import UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """获取用户统计信息"""
    user = request.user
    
    # 总事件数
    event_count = Event.objects.filter(user=user).count()
    
    # 今日事件数
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    today_count = Event.objects.filter(
        user=user,
        start_time__gte=today_start,
        start_time__lte=today_end
    ).count()
    
    # 即将到来的事件数（未来7天）
    upcoming_end = timezone.now() + timedelta(days=7)
    upcoming_count = Event.objects.filter(
        user=user,
        start_time__gte=timezone.now(),
        start_time__lte=upcoming_end
    ).count()
    
    return Response({
        'event_count': event_count,
        'today_count': today_count,
        'upcoming_count': upcoming_count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bindings(request):
    """获取用户的第三方账号绑定状态"""
    user = request.user
    
    # 检查是否有密码（普通注册的用户有密码）
    has_password = user.has_usable_password()
    
    # 检查第三方账号绑定
    has_acwing = hasattr(user, 'acwing_profile')
    has_qq = hasattr(user, 'qq_profile')
    
    return Response({
        'acwing': has_acwing,
        'qq': has_qq,
        'has_password': has_password
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新用户个人信息"""
    user = request.user
    username = request.data.get('username')
    email = request.data.get('email')
    
    # 更新用户名（检查是否被占用）
    if username and username != user.username:
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return Response({
                'error': '用户名已被占用'
            }, status=status.HTTP_400_BAD_REQUEST)
        user.username = username
    
    # 更新邮箱
    if email is not None:
        user.email = email
    
    user.save()
    
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            'error': '请提供旧密码和新密码'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证旧密码
    if not user.check_password(old_password):
        return Response({
            'error': '旧密码不正确'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 设置新密码
    user.set_password(new_password)
    user.save()
    
    return Response({'message': '密码修改成功'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unbind_acwing(request):
    """解绑 AcWing 账号"""
    user = request.user
    
    # 检查是否至少有一种登录方式
    has_password = user.has_usable_password()
    has_qq = hasattr(user, 'qq_profile')
    
    if not has_password and not has_qq:
        return Response({
            'error': '无法解绑：请至少保留一种登录方式'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 删除 AcWing 绑定
    if hasattr(user, 'acwing_profile'):
        user.acwing_profile.delete()
        return Response({'message': '解绑成功'})
    else:
        return Response({
            'error': '未绑定 AcWing 账号'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unbind_qq(request):
    """解绑 QQ 账号"""
    user = request.user
    
    # 检查是否至少有一种登录方式
    has_password = user.has_usable_password()
    has_acwing = hasattr(user, 'acwing_profile')
    
    if not has_password and not has_acwing:
        return Response({
            'error': '无法解绑：请至少保留一种登录方式'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 删除 QQ 绑定
    if hasattr(user, 'qq_profile'):
        user.qq_profile.delete()
        return Response({'message': '解绑成功'})
    else:
        return Response({
            'error': '未绑定 QQ 账号'
        }, status=status.HTTP_400_BAD_REQUEST)

