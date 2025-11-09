"""
API Views Package - 模块化视图导入

将所有视图函数和ViewSet导入到包级别，方便外部调用
"""

# ViewSets
from .events import EventViewSet
from .calendars import PublicCalendarViewSet

# Authentication Views
from .auth import register, get_current_user, acwing_login, qq_login, get_acwing_login_url, get_qq_login_url

# User Profile Views
from .user import get_user_stats, get_bindings, update_profile, change_password, unbind_acwing, unbind_qq

# OAuth Callback
from .oauth_callback import acwing_oauth_callback

# Utility Views
from .lunar import get_lunar_date
from .holidays import get_holidays, check_holiday, get_today_holidays

# Fusion Views (Roamio × Ralendar)
from .fusion import (
    batch_create_events,
    get_user_events,
    get_trip_events, 
    delete_trip_events,
    mark_notification_sent,
    get_events_with_location,
    get_roamio_events,
    sync_from_roamio
)

# 导出所有视图
__all__ = [
    'EventViewSet',
    'PublicCalendarViewSet',
    'register',
    'get_current_user',
    'acwing_login',
    'qq_login',
    'get_acwing_login_url',
    'get_qq_login_url',
    'get_user_stats',
    'get_bindings',
    'update_profile',
    'change_password',
    'unbind_acwing',
    'unbind_qq',
    'acwing_oauth_callback',
    'get_lunar_date',
    'get_holidays',
    'check_holiday',
    'get_today_holidays',
    # Fusion APIs
    'batch_create_events',
    'get_user_events',
    'get_trip_events',
    'delete_trip_events',
    'mark_notification_sent',
    'get_events_with_location',
    'get_roamio_events',
    'sync_from_roamio',
]

