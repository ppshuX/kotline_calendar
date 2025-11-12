"""
工具类路由
包括：农历转换、节假日查询、AI助手
"""
from django.urls import path
from ..views import (
    get_lunar_date,
    get_holidays,
    check_holiday,
    get_today_holidays,
)
from ..views import holidays
from ..views.ai_assistant import (
    parse_event_from_text,
    summarize_schedule,
    chat_with_assistant,
)

urlpatterns = [
    # 农历转换
    path('lunar/', get_lunar_date, name='lunar'),
    
    # 节假日查询
    path('holidays/', get_holidays, name='get_holidays'),
    path('holidays/check/', check_holiday, name='check_holiday'),
    path('holidays/today/', get_today_holidays, name='get_today_holidays'),
    
    # 节日详情
    path('festivals/detail/', holidays.get_festival_detail, name='get_festival_detail'),
    
    # AI助手
    path('ai/parse-event/', parse_event_from_text, name='ai_parse_event'),
    path('ai/summarize/', summarize_schedule, name='ai_summarize'),
    path('ai/chat/', chat_with_assistant, name='ai_chat'),
]

