"""
Models - 数据模型模块
"""
from .user import AcWingUser, QQUser, UserMapping
from .event import Event
from .calendar import PublicCalendar
from .calendar_data import Holiday, LunarCalendar, DailyFortune, UserFortune, DataSyncLog
from .oauth import OAuthClient, AuthorizationCode, OAuthAccessToken, OAUTH_SCOPES, get_scope_description

__all__ = [
    'AcWingUser',
    'QQUser',
    'UserMapping',
    'Event',
    'PublicCalendar',
    'Holiday',
    'LunarCalendar',
    'DailyFortune',
    'UserFortune',
    'DataSyncLog',
    'OAuthClient',
    'AuthorizationCode',
    'OAuthAccessToken',
    'OAUTH_SCOPES',
    'get_scope_description',
]

