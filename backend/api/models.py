from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """日程事件"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name='用户'
    )
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    location = models.CharField(max_length=200, blank=True, verbose_name='地点')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['start_time']
        verbose_name = '日程'
        verbose_name_plural = '日程列表'
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class PublicCalendar(models.Model):
    """公开日历（用于订阅）"""
    name = models.CharField(max_length=100, verbose_name='日历名称')
    url_slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='描述')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='创建者'
    )
    events = models.ManyToManyField(
        Event, 
        blank=True, 
        related_name='calendars',
        verbose_name='日程列表'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '公开日历'
        verbose_name_plural = '公开日历列表'
    
    def __str__(self):
        return self.name
