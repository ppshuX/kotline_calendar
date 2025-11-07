"""
Public Calendars API - 公开日历管理
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import PublicCalendar
from ..serializers import PublicCalendarSerializer


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
    
    def generate_ics(self, calendar):
        """生成 iCalendar 格式"""
        events = calendar.events.all()
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:-//KotlinCalendar//{calendar.name}//CN",
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

