"""
API Views Package - 模块化视图导入

将所有视图函数和ViewSet导入到包级别，方便外部调用
"""

# ViewSets
from .events import EventViewSet
from .calendars import PublicCalendarViewSet

# Authentication Views
from .auth import register, get_current_user, acwing_login

# Utility Views
from .lunar import get_lunar_date

# 导出所有视图
__all__ = [
    'EventViewSet',
    'PublicCalendarViewSet',
    'register',
    'get_current_user',
    'acwing_login',
    'get_lunar_date',
]

