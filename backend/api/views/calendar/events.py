"""
Events API - 日程事件管理
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

from ..models import Event
from ..serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """日程 CRUD API"""
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # 允许所有人访问，未登录用户使用匿名账户
    
    def get_queryset(self):
        """只返回当前用户的日程（如果已登录）"""
        if self.request.user.is_authenticated:
            return Event.objects.filter(user=self.request.user)
        # 开发环境：返回所有日程
        return Event.objects.all()
    
    def perform_create(self, serializer):
        """创建日程时关联用户"""
        if self.request.user.is_authenticated:
            # 用户已登录，关联当前用户
            serializer.save(user=self.request.user)
        else:
            # 开发环境：使用默认用户或创建匿名用户
            default_user, _ = User.objects.get_or_create(username='anonymous')
            serializer.save(user=default_user)

