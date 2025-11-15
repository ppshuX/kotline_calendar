"""
API Views Package - 模块化视图导入

将所有视图函数和ViewSet导入到包级别，方便外部调用

重构说明：
- auth/: 认证相关（auth.py, oauth_callback.py, user.py）
- calendar/: 日历核心（calendars.py, events.py）
- external/: 外部服务（holidays.py, lunar.py, weather.py）
- ai/: AI助手（assistant.py）
- integration/: 第三方集成（fusion.py）
- oauth/: OAuth 2.0 服务器（authorize.py, token.py, userinfo.py, revoke.py）
"""

# Calendar Core - ViewSets
from .calendar.events import EventViewSet
from .calendar.calendars import PublicCalendarViewSet

# Authentication
from .auth.auth import get_current_user, acwing_login, qq_login, get_acwing_login_url, get_qq_login_url

# User Profile
from .auth.user import get_user_stats, get_bindings, update_profile, change_password, unbind_acwing, unbind_qq

# OAuth Callback
from .auth.oauth_callback import acwing_oauth_callback

# OAuth 2.0 Server
from .oauth.authorize import oauth_authorize
from .oauth.token import oauth_token
from .oauth.userinfo import oauth_userinfo
from .oauth.revoke import oauth_revoke, oauth_authorized_apps

# External Services
from .external.lunar import get_lunar_date
from .external.holidays import get_holidays, check_holiday, get_today_holidays
from .external.fortune import get_today_fortune

# Third-party Integration
from .integration.fusion import (
    batch_create_events,
    get_user_events,
    manage_event,
    get_trip_events, 
    delete_trip_events,
    mark_notification_sent,
    get_events_with_location,
    get_roamio_events,
    sync_from_roamio,
    check_email_availability
)

# 导出所有视图
__all__ = [
    # Calendar
    'EventViewSet',
    'PublicCalendarViewSet',
    # Authentication
    'get_current_user',
    'acwing_login',
    'qq_login',
    'get_acwing_login_url',
    'get_qq_login_url',
    # User Profile
    'get_user_stats',
    'get_bindings',
    'update_profile',
    'change_password',
    'unbind_acwing',
    'unbind_qq',
    # OAuth Callback
    'acwing_oauth_callback',
    # OAuth 2.0 Server
    'oauth_authorize',
    'oauth_token',
    'oauth_userinfo',
    'oauth_revoke',
    'oauth_authorized_apps',
    # External Services
    'get_lunar_date',
    'get_holidays',
    'check_holiday',
    'get_today_holidays',
    'get_today_fortune',
    # Fusion APIs
    'batch_create_events',
    'get_user_events',
    'manage_event',
    'get_trip_events',
    'delete_trip_events',
    'mark_notification_sent',
    'get_events_with_location',
    'get_roamio_events',
    'sync_from_roamio',
    'check_email_availability',
]

