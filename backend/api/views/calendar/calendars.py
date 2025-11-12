"""
Public Calendars API - 公开日历管理
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import PublicCalendar, Event
from ..serializers import PublicCalendarSerializer, EventSerializer


class PublicCalendarViewSet(viewsets.ReadOnlyModelViewSet):
    """公开日历 API（只读）"""
    queryset = PublicCalendar.objects.filter(is_public=True)
    serializer_class = PublicCalendarSerializer
    lookup_field = 'url_slug'
    
    @action(detail=False, methods=['get'], url_path='available')
    def available_calendars(self, request):
        """获取所有可订阅的日历列表（Android使用）"""
        calendars = PublicCalendar.objects.filter(is_public=True)
        
        # 日历元数据（颜色和图标）
        calendar_metadata = {
            'china-holidays': {
                'color': '#FF6B6B',
                'icon': '🏮'
            },
            'lunar-festivals': {
                'color': '#4ECDC4',
                'icon': '🎊'
            },
            'world-days': {
                'color': '#95E1D3',
                'icon': '🌍'
            }
        }
        
        calendars_data = []
        for calendar in calendars:
            metadata = calendar_metadata.get(calendar.url_slug, {
                'color': '#667eea',
                'icon': '📅'
            })
            
            calendars_data.append({
                'id': calendar.id,
                'name': calendar.name,
                'slug': calendar.url_slug,
                'description': calendar.description,
                'color': metadata['color'],
                'icon': metadata['icon'],
                'event_count': calendar.events.count(),
                'is_public': calendar.is_public
            })
        
        return Response({
            'success': True,
            'calendars': calendars_data
        })
    
    @action(detail=True, methods=['get'])
    def feed(self, request, url_slug=None):
        """返回 iCalendar 格式的日历订阅"""
        calendar = self.get_object()
        ics_content = self.generate_ics(calendar)
        return Response(
            {'ics': ics_content, 'events_count': calendar.events.count()},
            content_type='application/json'
        )
    
    @action(detail=True, methods=['get'], url_path='events-json')
    def events_json(self, request, url_slug=None):
        """返回 JSON 格式的日历事件列表（Android 订阅使用）"""
        calendar = self.get_object()
        events = calendar.events.all().order_by('start_time')
        
        # 序列化事件数据
        events_data = []
        for event in events:
            # 判断是否为全天事件（开始和结束时间都是整点且相差24小时）
            is_all_day = False
            if event.end_time:
                time_diff = event.end_time - event.start_time
                is_all_day = (time_diff.days >= 1 and 
                             event.start_time.hour == 0 and 
                             event.start_time.minute == 0)
            
            events_data.append({
                'title': event.title,
                'description': event.description or '',
                'location': event.location or '',
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat() if event.end_time else event.start_time.isoformat(),
                'all_day': is_all_day,
                'reminder_minutes': event.reminder_minutes,
            })
        
        return Response({
            'calendar_name': calendar.name,
            'calendar_description': calendar.description,
            'events_count': len(events_data),
            'events': events_data
        })
    
    def generate_ics(self, calendar):
        """生成 iCalendar 格式"""
        events = calendar.events.all()
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:-//Ralendar//{calendar.name}//CN",
            f"X-WR-CALNAME:{calendar.name}",
        ]
        
        for event in events:
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:event-{event.id}@kotlincalendar.com",
                f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{event.title}",
                f"DESCRIPTION:{event.description}",
                f"LOCATION:{event.location}",
                "END:VEVENT",
            ])
        
        ics_lines.append("END:VCALENDAR")
        return "\n".join(ics_lines)

