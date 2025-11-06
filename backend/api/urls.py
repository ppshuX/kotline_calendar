from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('events', views.EventViewSet, basename='event')
router.register('calendars', views.PublicCalendarViewSet, basename='calendar')

urlpatterns = [
    # REST API
    path('', include(router.urls)),
    
    # 用户认证
    path('auth/register/', views.register, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.get_current_user, name='current_user'),
    
    # 农历
    path('lunar/', views.get_lunar_date, name='lunar'),
]

