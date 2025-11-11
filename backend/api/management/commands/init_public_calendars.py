"""
初始化公开日历数据
用法：python manage.py init_public_calendars
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import PublicCalendar, Event, Holiday
from django.utils import timezone
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = '初始化公开日历数据（中国法定节假日等）'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化公开日历数据...'))
        
        # 1. 获取或创建系统用户
        admin_user, created = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@ralendar.com'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ 创建系统用户'))
        
        # 2. 创建"中国法定节假日"日历
        china_holidays, created = PublicCalendar.objects.get_or_create(
            url_slug='china-holidays',
            defaults={
                'name': '中国法定节假日',
                'description': '2025年中国法定节假日和调休安排',
                'created_by': admin_user,
                'is_public': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ 创建"中国法定节假日"日历'))
            
            # 添加2025年节假日事件
            holidays_2025 = [
                ('元旦', '2025-01-01', '2025-01-01'),
                ('春节', '2025-01-28', '2025-02-04'),  # 7天假期
                ('清明节', '2025-04-04', '2025-04-06'),  # 3天假期
                ('劳动节', '2025-05-01', '2025-05-05'),  # 5天假期
                ('端午节', '2025-05-31', '2025-06-02'),  # 3天假期
                ('中秋节', '2025-10-06', '2025-10-08'),  # 3天假期
                ('国庆节', '2025-10-01', '2025-10-08'),  # 8天假期（含中秋）
            ]
            
            for name, start, end in holidays_2025:
                start_time = timezone.make_aware(datetime.strptime(f"{start} 00:00", '%Y-%m-%d %H:%M'))
                end_time = timezone.make_aware(datetime.strptime(f"{end} 23:59", '%Y-%m-%d %H:%M'))
                
                event = Event.objects.create(
                    user=admin_user,
                    title=f"🎉 {name}",
                    description=f"2025年{name}假期",
                    start_time=start_time,
                    end_time=end_time,
                    location='',
                    source_app='ralendar',
                )
                china_holidays.events.add(event)
                self.stdout.write(f'    添加节日：{name}')
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ 添加了 {len(holidays_2025)} 个节假日'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  "中国法定节假日"日历已存在'))
        
        # 3. 创建"农历节气"日历
        lunar_calendar, created = PublicCalendar.objects.get_or_create(
            url_slug='lunar-festivals',
            defaults={
                'name': '农历传统节日',
                'description': '2025年农历传统节日',
                'created_by': admin_user,
                'is_public': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ 创建"农历传统节日"日历'))
            
            # 农历节日（2025年对应公历日期）
            lunar_festivals = [
                ('除夕', '2025-01-28', '🏮'),
                ('春节', '2025-01-29', '🧨'),
                ('元宵节', '2025-02-12', '🏮'),
                ('端午节', '2025-05-31', '🐉'),
                ('七夕节', '2025-08-29', '💕'),
                ('中秋节', '2025-10-06', '🥮'),
                ('重阳节', '2025-10-29', '🍵'),
                ('腊八节', '2026-01-07', '🍜'),
            ]
            
            for name, date_str, emoji in lunar_festivals:
                start_time = timezone.make_aware(datetime.strptime(f"{date_str} 00:00", '%Y-%m-%d %H:%M'))
                end_time = timezone.make_aware(datetime.strptime(f"{date_str} 23:59", '%Y-%m-%d %H:%M'))
                
                event = Event.objects.create(
                    user=admin_user,
                    title=f"{emoji} {name}",
                    description=f"农历传统节日",
                    start_time=start_time,
                    end_time=end_time,
                    location='',
                    source_app='ralendar',
                )
                lunar_calendar.events.add(event)
                self.stdout.write(f'    添加节日：{name}')
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ 添加了 {len(lunar_festivals)} 个传统节日'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  "农历传统节日"日历已存在'))
        
        # 4. 创建"国际纪念日"日历
        world_days, created = PublicCalendar.objects.get_or_create(
            url_slug='world-days',
            defaults={
                'name': '国际纪念日',
                'description': '重要的国际纪念日',
                'created_by': admin_user,
                'is_public': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ 创建"国际纪念日"日历'))
            
            international_days = [
                ('情人节', '2025-02-14', '💕'),
                ('妇女节', '2025-03-08', '👩'),
                ('愚人节', '2025-04-01', '🤡'),
                ('地球日', '2025-04-22', '🌍'),
                ('儿童节', '2025-06-01', '🧒'),
                ('教师节', '2025-09-10', '📚'),
                ('万圣节', '2025-10-31', '🎃'),
                ('感恩节', '2025-11-27', '🦃'),
                ('平安夜', '2025-12-24', '🎄'),
                ('圣诞节', '2025-12-25', '🎅'),
            ]
            
            for name, date_str, emoji in international_days:
                start_time = timezone.make_aware(datetime.strptime(f"{date_str} 00:00", '%Y-%m-%d %H:%M'))
                end_time = timezone.make_aware(datetime.strptime(f"{date_str} 23:59", '%Y-%m-%d %H:%M'))
                
                event = Event.objects.create(
                    user=admin_user,
                    title=f"{emoji} {name}",
                    description=f"国际纪念日",
                    start_time=start_time,
                    end_time=end_time,
                    location='',
                    source_app='ralendar',
                )
                world_days.events.add(event)
                self.stdout.write(f'    添加节日：{name}')
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ 添加了 {len(international_days)} 个国际纪念日'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  "国际纪念日"日历已存在'))
        
        # 统计
        total_calendars = PublicCalendar.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n✅ 完成！共有 {total_calendars} 个公开日历'))
        self.stdout.write(self.style.SUCCESS('\n可用的订阅URL：'))
        for cal in PublicCalendar.objects.filter(is_public=True):
            self.stdout.write(f'  - {cal.url_slug}: {cal.name} ({cal.events.count()}个事件)')

