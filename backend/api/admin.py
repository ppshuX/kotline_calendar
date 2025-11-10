"""
Django Admin 配置
提供可视化的数据管理界面
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Event, 
    QQUser, 
    Holiday, 
    LunarCalendar, 
    DailyFortune, 
    UserFortune, 
    DataSyncLog
)


# ============================================================
# 节假日管理
# ============================================================
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """节假日管理"""
    
    list_display = [
        'colored_date',
        'emoji_name', 
        'colored_type',
        'is_legal_holiday', 
        'is_rest_day',
        'holiday_group'
    ]
    
    list_filter = [
        'type',
        'is_legal_holiday', 
        'is_rest_day',
        'is_workday',
        ('date', admin.DateFieldListFilter),
    ]
    
    search_fields = ['name', 'description', 'holiday_group']
    
    ordering = ['-date']
    
    date_hierarchy = 'date'
    
    readonly_fields = ['last_updated', 'data_version']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('date', 'name', 'type', 'emoji')
        }),
        ('属性', {
            'fields': ('is_legal_holiday', 'is_rest_day', 'is_workday', 'holiday_group')
        }),
        ('农历信息', {
            'fields': ('lunar_date',),
            'classes': ('collapse',)
        }),
        ('描述', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('data_version', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_legal_holiday', 'mark_as_rest_day']
    
    def colored_date(self, obj):
        """带颜色的日期"""
        color = '#e74c3c' if obj.is_legal_holiday else '#3498db'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.date
        )
    colored_date.short_description = '日期'
    colored_date.admin_order_field = 'date'
    
    def emoji_name(self, obj):
        """带 Emoji 的名称"""
        return f"{obj.emoji} {obj.name}"
    emoji_name.short_description = '名称'
    emoji_name.admin_order_field = 'name'
    
    def colored_type(self, obj):
        """带颜色的类型"""
        colors = {
            'major': '#e74c3c',
            'vacation': '#3498db',
            'traditional': '#f39c12',
            'international': '#9b59b6',
        }
        color = colors.get(obj.type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_type_display()
        )
    colored_type.short_description = '类型'
    colored_type.admin_order_field = 'type'
    
    def mark_as_legal_holiday(self, request, queryset):
        """批量标记为法定假日"""
        updated = queryset.update(is_legal_holiday=True)
        self.message_user(request, f'成功标记 {updated} 条记录为法定假日')
    mark_as_legal_holiday.short_description = '标记为法定假日'
    
    def mark_as_rest_day(self, request, queryset):
        """批量标记为休息日"""
        updated = queryset.update(is_rest_day=True)
        self.message_user(request, f'成功标记 {updated} 条记录为休息日')
    mark_as_rest_day.short_description = '标记为休息日'


# ============================================================
# 数据同步日志
# ============================================================
@admin.register(DataSyncLog)
class DataSyncLogAdmin(admin.ModelAdmin):
    """数据同步日志"""
    
    list_display = [
        'colored_data_type',
        'date_range',
        'colored_status',
        'records_count',
        'created_at_display'
    ]
    
    list_filter = [
        'data_type',
        'status',
        ('created_at', admin.DateFieldListFilter),
    ]
    
    search_fields = ['error_message']
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'data_type',
        'sync_date',
        'sync_date_end',
        'status',
        'records_count',
        'error_message',
        'started_at',
        'completed_at',
        'created_at'
    ]
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """允许删除旧日志"""
        return True
    
    def colored_data_type(self, obj):
        """带颜色的数据类型"""
        colors = {
            'holiday': '#3498db',
            'lunar': '#f39c12',
            'fortune': '#9b59b6',
        }
        color = colors.get(obj.data_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_data_type_display()
        )
    colored_data_type.short_description = '数据类型'
    colored_data_type.admin_order_field = 'data_type'
    
    def date_range(self, obj):
        """日期范围"""
        if obj.sync_date_end:
            return f"{obj.sync_date} ~ {obj.sync_date_end}"
        return str(obj.sync_date)
    date_range.short_description = '同步范围'
    
    def colored_status(self, obj):
        """带颜色的状态"""
        colors = {
            'pending': '#95a5a6',
            'syncing': '#3498db',
            'success': '#27ae60',
            'failed': '#e74c3c',
        }
        icons = {
            'pending': '⏳',
            'syncing': '🔄',
            'success': '✅',
            'failed': '❌',
        }
        color = colors.get(obj.status, '#95a5a6')
        icon = icons.get(obj.status, '•')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    colored_status.short_description = '状态'
    colored_status.admin_order_field = 'status'
    
    def created_at_display(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = '创建时间'
    created_at_display.admin_order_field = 'created_at'


# ============================================================
# 事件管理
# ============================================================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """事件管理"""
    
    list_display = [
        'title',
        'user_link',
        'start_time_display',
        'is_from_roamio_icon',
        'email_reminder_icon',
        'notification_sent_icon'
    ]
    
    list_filter = [
        'source_app',
        'email_reminder',
        'notification_sent',
        ('start_time', admin.DateFieldListFilter),
    ]
    
    search_fields = ['title', 'description', 'location', 'user__username']
    
    ordering = ['-start_time']
    
    date_hierarchy = 'start_time'
    
    readonly_fields = ['created_at', 'related_trip_slug', 'source_app', 'source_id']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'title', 'description', 'start_time', 'end_time')
        }),
        ('位置信息', {
            'fields': ('has_location', 'location', 'latitude', 'longitude', 'map_url'),
            'classes': ('collapse',)
        }),
        ('提醒设置', {
            'fields': ('email_reminder', 'reminder_minutes', 'notification_sent')
        }),
        ('来源信息', {
            'fields': ('source_app', 'source_id', 'related_trip_slug'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_email_reminder', 'disable_email_reminder', 'reset_notification']
    
    def user_link(self, obj):
        """用户链接"""
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = '用户'
    user_link.admin_order_field = 'user__username'
    
    def start_time_display(self, obj):
        """格式化开始时间"""
        from django.utils import timezone
        local_time = timezone.localtime(obj.start_time)
        return local_time.strftime('%Y-%m-%d %H:%M')
    start_time_display.short_description = '开始时间'
    start_time_display.admin_order_field = 'start_time'
    
    def is_from_roamio_icon(self, obj):
        """Roamio 图标"""
        if obj.is_from_roamio:
            return format_html('<span style="color: #27ae60;">✅ 是</span>')
        return format_html('<span style="color: #95a5a6;">—</span>')
    is_from_roamio_icon.short_description = 'Roamio'
    is_from_roamio_icon.admin_order_field = 'is_from_roamio'
    
    def email_reminder_icon(self, obj):
        """邮件提醒图标"""
        if obj.email_reminder:
            return format_html('<span style="color: #3498db;">📧 {}分钟</span>', obj.reminder_minutes)
        return format_html('<span style="color: #95a5a6;">—</span>')
    email_reminder_icon.short_description = '邮件提醒'
    email_reminder_icon.admin_order_field = 'email_reminder'
    
    def notification_sent_icon(self, obj):
        """通知发送状态"""
        if obj.notification_sent:
            return format_html('<span style="color: #27ae60;">✅ 已发送</span>')
        elif obj.email_reminder:
            return format_html('<span style="color: #f39c12;">⏳ 待发送</span>')
        return format_html('<span style="color: #95a5a6;">—</span>')
    notification_sent_icon.short_description = '通知状态'
    notification_sent_icon.admin_order_field = 'notification_sent'
    
    def enable_email_reminder(self, request, queryset):
        """批量启用邮件提醒"""
        updated = queryset.update(email_reminder=True)
        self.message_user(request, f'成功为 {updated} 个事件启用邮件提醒')
    enable_email_reminder.short_description = '启用邮件提醒'
    
    def disable_email_reminder(self, request, queryset):
        """批量禁用邮件提醒"""
        updated = queryset.update(email_reminder=False)
        self.message_user(request, f'成功为 {updated} 个事件禁用邮件提醒')
    disable_email_reminder.short_description = '禁用邮件提醒'
    
    def reset_notification(self, request, queryset):
        """重置通知状态"""
        updated = queryset.update(notification_sent=False)
        self.message_user(request, f'成功重置 {updated} 个事件的通知状态')
    reset_notification.short_description = '重置通知状态'


# ============================================================
# QQ 用户管理
# ============================================================
@admin.register(QQUser)
class QQUserAdmin(admin.ModelAdmin):
    """QQ 用户信息"""
    
    list_display = [
        'user_link',
        'openid_display',
        'unionid_display',
        'has_avatar'
    ]
    
    search_fields = ['openid', 'unionid', 'user__username']
    
    readonly_fields = ['openid', 'unionid', 'photo_url']
    
    def user_link(self, obj):
        """用户链接"""
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = '用户'
    user_link.admin_order_field = 'user__username'
    
    def openid_display(self, obj):
        """OpenID 显示（脱敏）"""
        if obj.openid:
            return f"{obj.openid[:8]}...{obj.openid[-8:]}"
        return '—'
    openid_display.short_description = 'OpenID'
    
    def unionid_display(self, obj):
        """UnionID 显示（脱敏）"""
        if obj.unionid:
            return f"{obj.unionid[:12]}...{obj.unionid[-8:]}"
        return '—'
    unionid_display.short_description = 'UnionID'
    
    def has_avatar(self, obj):
        """是否有头像"""
        if obj.photo_url:
            return format_html('<span style="color: #27ae60;">✅</span>')
        return format_html('<span style="color: #95a5a6;">—</span>')
    has_avatar.short_description = '头像'


# ============================================================
# 自定义 User Admin
# ============================================================
class QQUserInline(admin.StackedInline):
    """在用户页面显示 QQ 信息"""
    model = QQUser
    can_delete = False
    verbose_name = 'QQ 账号信息'
    verbose_name_plural = 'QQ 账号信息'
    readonly_fields = ['openid', 'unionid', 'photo_url']
    
    def has_add_permission(self, request, obj=None):
        """不允许在这里添加 QQ 账号"""
        return False


class CustomUserAdmin(BaseUserAdmin):
    """自定义用户管理"""
    inlines = [QQUserInline]
    
    list_display = [
        'username',
        'email',
        'event_count',
        'is_staff',
        'is_active',
        'date_joined_display'
    ]
    
    def event_count(self, obj):
        """事件数量"""
        try:
            count = obj.events.count()
            if count > 0:
                return format_html(
                    '<a href="/admin/api/event/?user__id__exact={}">{} 个</a>',
                    obj.id,
                    count
                )
            return '0'
        except Exception as e:
            return '—'
    event_count.short_description = '事件数'
    
    def date_joined_display(self, obj):
        """注册时间"""
        return obj.date_joined.strftime('%Y-%m-%d')
    date_joined_display.short_description = '注册时间'
    date_joined_display.admin_order_field = 'date_joined'


# 重新注册 User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============================================================
# 其他模型（黄历、运势等）
# ============================================================
@admin.register(LunarCalendar)
class LunarCalendarAdmin(admin.ModelAdmin):
    """农历管理"""
    list_display = ['date', 'lunar_date_cn', 'zodiac']
    list_filter = [('date', admin.DateFieldListFilter)]
    search_fields = ['lunar_date_cn', 'zodiac']
    ordering = ['-date']


@admin.register(DailyFortune)
class DailyFortuneAdmin(admin.ModelAdmin):
    """每日运势管理"""
    list_display = ['date', 'lucky_color', 'lucky_number']
    list_filter = [('date', admin.DateFieldListFilter)]
    ordering = ['-date']


@admin.register(UserFortune)
class UserFortuneAdmin(admin.ModelAdmin):
    """用户运势配置"""
    list_display = ['user', 'zodiac', 'constellation']
    search_fields = ['user__username', 'zodiac', 'constellation']


# ============================================================
# 自定义 Admin 站点标题
# ============================================================
admin.site.site_header = 'Ralendar 管理后台'
admin.site.site_title = 'Ralendar Admin'
admin.site.index_title = '欢迎使用 Ralendar 管理系统'
