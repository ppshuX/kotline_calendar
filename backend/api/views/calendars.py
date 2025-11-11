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
            events_data.append({
                'title': event.title,
                'description': event.description or '',
                'location': event.location or '',
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat(),
                'all_day': event.all_day,
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

