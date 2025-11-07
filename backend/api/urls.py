from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    EventViewSet,
    PublicCalendarViewSet,
    register,
    get_current_user,
    acwing_login,
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
    path('auth/acwing/login/', acwing_login, name='acwing_login'),
    
    # 农历
    path('lunar/', get_lunar_date, name='lunar'),
]

