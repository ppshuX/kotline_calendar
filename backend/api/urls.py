"""
API 主路由配置（模块化版本）

路由已按功能模块拆分到 url_patterns/ 目录：
- auth.py: 认证相关（注册、登录、OAuth）
- user.py: 用户中心（统计、绑定、个人信息）
- fusion.py: 融合相关（Roamio × Ralendar）
- utils.py: 工具类（农历、节假日）
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, PublicCalendarViewSet, acwing_oauth_callback

# DRF Router - 处理 RESTful API
router = DefaultRouter()
router.register('events', EventViewSet, basename='event')
router.register('calendars', PublicCalendarViewSet, basename='calendar')

urlpatterns = [
    # RESTful API (ViewSet)
    path('', include(router.urls)),
    
    # 认证相关路由
    path('auth/', include('api.url_patterns.auth')),
    
    # 用户中心路由
    path('user/', include('api.url_patterns.user')),
    
    # OAuth 2.0 路由（第三方应用接入）
    path('oauth/', include('api.url_patterns.oauth')),
    
    # 融合功能路由 (Roamio × Ralendar)
    path('fusion/', include('api.url_patterns.fusion')),
    
    # 工具类路由 (农历、节假日)
    path('', include('api.url_patterns.utils')),
    
    # AcWing OAuth 特殊回调（需要保持在根路径）
    path('oauth2/receive_code/', acwing_oauth_callback, name='acwing_oauth_callback'),
]

