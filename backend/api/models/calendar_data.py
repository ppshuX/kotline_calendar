"""
日历相关数据模型
包括：节假日、黄历、运势等
"""
from django.db import models
from django.contrib.auth.models import User


class Holiday(models.Model):
    """
    法定节假日和传统节日
    
    数据范围：往前 1 年，往后 3 年（共 4 年）
    更新频率：每年 1 月自动更新
    """
    date = models.DateField(db_index=True, help_text="日期")
    name = models.CharField(max_length=50, help_text="节日名称，如'春节'")
    type = models.CharField(max_length=20, choices=[
        ('major', '主要节日'),           # 节日当天
        ('vacation', '假期'),            # 假期中的其他天
        ('traditional', '传统节日'),      # 农历节日
        ('international', '国际节日'),    # 情人节、圣诞节等
    ], help_text="节日类型")
    
    is_legal_holiday = models.BooleanField(default=False, help_text="是否法定假日")
    is_rest_day = models.BooleanField(default=False, help_text="是否休息日")
    is_workday = models.BooleanField(default=False, help_text="是否调休工作日")
    
    # 关联信息
    holiday_group = models.CharField(max_length=50, null=True, blank=True, 
                                     help_text="假期组名，如'春节假期'")
    lunar_date = models.CharField(max_length=20, null=True, blank=True,
                                  help_text="农历日期，如'正月初一'")
    
    # 元数据
    description = models.TextField(null=True, blank=True, help_text="节日介绍")
    emoji = models.CharField(max_length=10, default='🎉', help_text="Emoji 图标")
    
    # 数据版本
    data_version = models.CharField(max_length=20, default='1.0', help_text="数据版本")
    last_updated = models.DateTimeField(auto_now=True, help_text="最后更新时间")
    
    class Meta:
        db_table = 'calendar_holidays'
        unique_together = ('date', 'name', 'type')
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['is_legal_holiday']),
        ]
        verbose_name = '节假日'
        verbose_name_plural = '节假日列表'
    
    def __str__(self):
        return f"{self.date} - {self.name}"


class LunarCalendar(models.Model):
    """
    黄历数据（宜忌、冲煞、吉神凶煞等）
    
    数据范围：当前年 + 未来 1 年（共 2 年，约 730 条）
    更新频率：每年 12 月自动更新下一年数据
    """
    date = models.DateField(unique=True, db_index=True, help_text="公历日期")
    
    # 农历信息
    lunar_year = models.IntegerField(help_text="农历年份")
    lunar_month = models.CharField(max_length=10, help_text="农历月份，如'正月'")
    lunar_day = models.CharField(max_length=10, help_text="农历日期，如'初一'")
    lunar_date_cn = models.CharField(max_length=50, help_text="农历日期中文，如'甲辰年正月初一'")
    
    # 生肖和天干地支
    zodiac = models.CharField(max_length=2, help_text="生肖，如'龙'")
    ganzhi_year = models.CharField(max_length=4, help_text="年干支，如'甲辰'")
    ganzhi_month = models.CharField(max_length=4, help_text="月干支")
    ganzhi_day = models.CharField(max_length=4, help_text="日干支")
    
    # 节气
    solar_term = models.CharField(max_length=10, null=True, blank=True, 
                                  help_text="节气，如'立春'")
    
    # 宜忌
    yi = models.JSONField(default=list, help_text="宜（适合做的事）")
    ji = models.JSONField(default=list, help_text="忌（不宜做的事）")
    
    # 冲煞
    chong = models.CharField(max_length=20, null=True, blank=True, 
                            help_text="相冲生肖，如'冲鼠'")
    sha = models.CharField(max_length=20, null=True, blank=True,
                          help_text="煞方位，如'煞北'")
    
    # 神煞
    ji_shen = models.JSONField(default=list, help_text="吉神")
    xiong_shen = models.JSONField(default=list, help_text="凶神")
    
    # 五行
    wu_xing = models.CharField(max_length=20, null=True, blank=True,
                               help_text="五行，如'金'")
    
    # 吉凶等级（1-5 星）
    auspicious_level = models.IntegerField(default=3, 
                                          help_text="吉凶等级：1=大凶, 3=平, 5=大吉")
    
    # 数据版本
    data_version = models.CharField(max_length=20, default='1.0')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_lunar_calendars'
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['lunar_year', 'lunar_month']),
            models.Index(fields=['auspicious_level']),
        ]
        verbose_name = '黄历'
        verbose_name_plural = '黄历列表'
    
    def __str__(self):
        return f"{self.date} - {self.lunar_date_cn}"
    
    @property
    def yi_display(self):
        """宜的事项（中文）"""
        return '、'.join(self.yi) if self.yi else '无'
    
    @property
    def ji_display(self):
        """忌的事项（中文）"""
        return '、'.join(self.ji) if self.ji else '无'


class DailyFortune(models.Model):
    """
    每日运势（星座 + 生肖）
    
    数据范围：当天 + 未来 7 天
    更新频率：每天凌晨自动更新
    """
    date = models.DateField(db_index=True, help_text="日期")
    fortune_type = models.CharField(max_length=20, choices=[
        ('zodiac', '生肖运势'),
        ('constellation', '星座运势'),
    ], help_text="运势类型")
    
    # 生肖 or 星座
    zodiac = models.CharField(max_length=2, null=True, blank=True,
                             help_text="生肖，如'龙'")
    constellation = models.CharField(max_length=20, null=True, blank=True,
                                    help_text="星座，如'天蝎座'")
    
    # 综合运势
    overall_score = models.IntegerField(default=50, help_text="综合运势评分（0-100）")
    summary = models.TextField(help_text="运势总结")
    
    # 分项运势
    love_score = models.IntegerField(default=50, help_text="爱情运势（0-100）")
    career_score = models.IntegerField(default=50, help_text="事业运势（0-100）")
    wealth_score = models.IntegerField(default=50, help_text="财运（0-100）")
    health_score = models.IntegerField(default=50, help_text="健康运势（0-100）")
    
    # 幸运元素
    lucky_color = models.CharField(max_length=20, null=True, blank=True,
                                   help_text="幸运颜色")
    lucky_number = models.CharField(max_length=20, null=True, blank=True,
                                    help_text="幸运数字")
    lucky_direction = models.CharField(max_length=20, null=True, blank=True,
                                       help_text="幸运方位")
    
    # 建议
    advice = models.TextField(null=True, blank=True, help_text="今日建议")
    
    # 数据来源
    data_source = models.CharField(max_length=50, default='auto', 
                                   help_text="数据来源：auto/api/user_input")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_fortunes'
        unique_together = ('date', 'fortune_type', 'zodiac', 'constellation')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'fortune_type']),
            models.Index(fields=['zodiac']),
            models.Index(fields=['constellation']),
        ]
        verbose_name = '运势'
        verbose_name_plural = '运势列表'
    
    def __str__(self):
        if self.zodiac:
            return f"{self.date} - {self.zodiac}运势"
        else:
            return f"{self.date} - {self.constellation}运势"


class UserFortune(models.Model):
    """
    用户个性化运势订阅
    
    用户可以订阅自己的生肖/星座运势
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='fortune_profile',
                                help_text="用户")
    
    # 个人信息
    birth_date = models.DateField(help_text="出生日期")
    zodiac = models.CharField(max_length=2, help_text="生肖")
    constellation = models.CharField(max_length=20, help_text="星座")
    
    # 订阅设置
    subscribe_zodiac = models.BooleanField(default=True, help_text="订阅生肖运势")
    subscribe_constellation = models.BooleanField(default=True, help_text="订阅星座运势")
    notify_daily = models.BooleanField(default=False, help_text="每日推送运势")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_user_fortunes'
        verbose_name = '用户运势配置'
        verbose_name_plural = '用户运势配置列表'
    
    def __str__(self):
        return f"{self.user.username} - {self.zodiac}/{self.constellation}"


class DataSyncLog(models.Model):
    """
    数据同步日志
    
    记录每次数据更新的状态
    """
    data_type = models.CharField(max_length=20, choices=[
        ('holiday', '节假日'),
        ('lunar', '黄历'),
        ('fortune', '运势'),
    ], help_text="数据类型")
    
    sync_date = models.DateField(help_text="同步日期范围开始")
    sync_date_end = models.DateField(null=True, blank=True, help_text="同步日期范围结束")
    
    status = models.CharField(max_length=20, choices=[
        ('pending', '待同步'),
        ('syncing', '同步中'),
        ('success', '成功'),
        ('failed', '失败'),
    ], default='pending', help_text="同步状态")
    
    records_count = models.IntegerField(default=0, help_text="同步记录数")
    error_message = models.TextField(null=True, blank=True, help_text="错误信息")
    
    # 时间戳
    started_at = models.DateTimeField(null=True, blank=True, help_text="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="完成时间")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'calendar_data_sync_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['data_type', 'status']),
            models.Index(fields=['sync_date']),
        ]
        verbose_name = '数据同步日志'
        verbose_name_plural = '数据同步日志列表'
    
    def __str__(self):
        return f"{self.data_type} - {self.sync_date} - {self.status}"

