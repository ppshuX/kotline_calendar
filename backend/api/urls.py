from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    EventViewSet,
    PublicCalendarViewSet,
    register,
    get_current_user,
    acwing_login,
    get_acwing_login_url,
    acwing_oauth_callback,
    qq_login,
    get_qq_login_url,
    get_user_stats,
    get_bindings,
    update_profile,
    change_password,
    unbind_acwing,
    unbind_qq,
    get_lunar_date,
)

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')
router.register('calendars', PublicCalendarViewSet, basename='calendar')

urlpatterns = [
    # REST API
    path('', include(router.urls)),
    
    # 用户认证
    path('auth/register/', register, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', get_current_user, name='current_user'),
    
    # AcWing 登录
    path('auth/acwing/login/', get_acwing_login_url, name='get_acwing_login_url'),  # GET: 获取授权 URL
    path('auth/acwing/callback/', acwing_login, name='acwing_login'),  # POST: 处理回调
    path('oauth2/receive_code/', acwing_oauth_callback, name='acwing_oauth_callback'),
    
    # QQ 登录
    path('auth/qq/login/', get_qq_login_url, name='get_qq_login_url'),  # GET: 获取授权 URL
    path('auth/qq/callback/', qq_login, name='qq_login'),  # POST: 处理回调
    
    # 用户个人中心
    path('user/stats/', get_user_stats, name='user_stats'),
    path('user/bindings/', get_bindings, name='user_bindings'),
    path('user/profile/', update_profile, name='update_profile'),
    path('user/change-password/', change_password, name='change_password'),
    path('user/unbind/acwing/', unbind_acwing, name='unbind_acwing'),
    path('user/unbind/qq/', unbind_qq, name='unbind_qq'),
    
    # 农历
    path('lunar/', get_lunar_date, name='lunar'),
]

