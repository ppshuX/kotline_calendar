"""
确保 Celery 应用在 Django 启动时加载
"""
from .celery import app as celery_app

__all__ = ('celery_app',)

