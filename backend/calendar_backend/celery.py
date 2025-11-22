"""
Celery 配置文件
用于异步任务处理（如邮件提醒）
"""
import os
from celery import Celery
from celery.schedules import crontab

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')

# 创建 Celery 应用
app = Celery('calendar_backend')

# 从 Django settings 中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 app 中的 tasks.py
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    # 每分钟检查一次即将到来的提醒
    'check-upcoming-reminders': {
        'task': 'api.tasks.check_and_send_reminders',
        'schedule': crontab(minute='*/1'),  # 每分钟执行一次
    },
    # 每月1号凌晨3点同步节假日数据
    'sync-holiday-data': {
        'task': 'api.tasks.sync_holiday_data',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),  # 每月1号 03:00
    },
}

# 时区配置
app.conf.timezone = 'Asia/Shanghai'



