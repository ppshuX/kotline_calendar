"""
Celery 异步任务
用于发送邮件提醒
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Event


@shared_task
def send_event_reminder_email(event_id):
    """
    发送单个事件的提醒邮件
    
    Args:
        event_id: 事件 ID
    
    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
    try:
        event = Event.objects.get(id=event_id)
        
        # 检查是否已发送
        if event.notification_sent:
            return False
        
        # 检查用户是否有邮箱
        if not event.user.email:
            print(f"用户 {event.user.username} 没有设置邮箱，跳过提醒")
            return False
        
        # 构建邮件内容
        subject = f"📅 日程提醒：{event.title}"
        
        # 格式化时间
        start_time = timezone.localtime(event.start_time).strftime('%Y年%m月%d日 %H:%M')
        
        # 构建位置信息
        location_info = ""
        if event.has_location:
            location_info = f"\n📍 地点：{event.location or '已设置地理位置'}"
            if event.map_url:
                location_info += f"\n🗺️ 导航：{event.map_url}"
        
        # 构建消息内容（纯文本版本）
        message = f"""
您好 {event.user.username}，

您有一个即将开始的日程：

📋 标题：{event.title}
⏰ 时间：{start_time}{location_info}

{f'📝 备注：{event.description}' if event.description else ''}

{'🔔 这是来自 Roamio 旅行计划的提醒' if event.is_from_roamio else ''}

---
Ralendar 日历系统
https://app7626.acapp.acwing.com.cn
        """
        
        # HTML 版本（更美观）
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
        .event-card {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .event-title {{ font-size: 20px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .event-info {{ margin: 10px 0; }}
        .event-info strong {{ color: #667eea; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📅 日程提醒</h2>
        </div>
        <div class="content">
            <p>您好 <strong>{event.user.username}</strong>，</p>
            <p>您有一个即将开始的日程：</p>
            
            <div class="event-card">
                <div class="event-title">📋 {event.title}</div>
                <div class="event-info"><strong>⏰ 时间：</strong>{start_time}</div>
                {f'<div class="event-info"><strong>📍 地点：</strong>{event.location or "已设置地理位置"}</div>' if event.has_location else ''}
                {f'<div class="event-info"><strong>📝 备注：</strong>{event.description}</div>' if event.description else ''}
                {f'<div class="event-info" style="color: #ff6b6b;">🔔 <strong>来自 Roamio 旅行计划</strong></div>' if event.is_from_roamio else ''}
                
                {f'<a href="{event.map_url}" class="button">🗺️ 查看地图导航</a>' if event.map_url else ''}
            </div>
            
            <p>祝您生活愉快！</p>
        </div>
        <div class="footer">
            <p>Ralendar 日历系统</p>
            <p><a href="https://app7626.acapp.acwing.com.cn" style="color: #667eea;">https://app7626.acapp.acwing.com.cn</a></p>
        </div>
    </div>
</body>
</html>
        """
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[event.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # 标记为已发送
        event.notification_sent = True
        event.save(update_fields=['notification_sent'])
        
        print(f"✅ 成功发送提醒邮件：{event.title} -> {event.user.email}")
        return True
        
    except Event.DoesNotExist:
        print(f"❌ 事件 {event_id} 不存在")
        return False
    except Exception as e:
        print(f"❌ 发送邮件失败：{str(e)}")
        return False


@shared_task
def check_and_send_reminders():
    """
    定时任务：检查即将到来的事件并发送提醒
    每分钟执行一次
    
    逻辑：
    1. 查找未来 N 分钟内开始的事件
    2. 过滤出：
       - 启用了邮件提醒（email_reminder=True）
       - 尚未发送通知（notification_sent=False）
       - 用户有邮箱地址
    3. 异步发送提醒邮件
    """
    now = timezone.now()
    advance_minutes = getattr(settings, 'REMINDER_ADVANCE_MINUTES', 15)
    
    # 计算时间范围：现在 到 未来 N 分钟
    reminder_start = now
    reminder_end = now + timedelta(minutes=advance_minutes)
    
    # 查找需要提醒的事件
    events_to_remind = Event.objects.filter(
        start_time__gte=reminder_start,
        start_time__lte=reminder_end,
        email_reminder=True,
        notification_sent=False,
        user__email__isnull=False,
        user__email__gt='',
    ).select_related('user')
    
    count = events_to_remind.count()
    
    if count > 0:
        print(f"🔔 发现 {count} 个需要提醒的事件")
        
        # 为每个事件创建异步任务
        for event in events_to_remind:
            send_event_reminder_email.delay(event.id)
            print(f"  - {event.title} ({event.start_time})")
    else:
        print(f"✓ 未来 {advance_minutes} 分钟内没有需要提醒的事件")
    
    return count

