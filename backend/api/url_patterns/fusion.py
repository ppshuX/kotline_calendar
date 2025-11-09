"""
融合相关路由 (Roamio × Ralendar)
包括：批量操作、旅行关联、特殊查询
"""
from django.urls import path
from ..views import (
    batch_create_events,
    get_user_events,
    update_event,
    delete_event,
    get_trip_events,
    delete_trip_events,
    mark_notification_sent,
    get_events_with_location,
    get_roamio_events,
    sync_from_roamio,
)

urlpatterns = [
    # 事件 CRUD（RESTful 风格，支持 UnionID）
    path('events/batch/', batch_create_events, name='batch_create_events'),  # 批量创建（特殊）
    path('events/', get_user_events, name='get_user_events'),  # GET 列表
    path('events/<int:event_id>/', update_event, name='update_event'),  # PUT 更新
    path('events/<int:event_id>/', delete_event, name='delete_event'),  # DELETE 删除（同一URL）
    path('sync/from-roamio/', sync_from_roamio, name='sync_from_roamio'),
    
    # 按旅行查询
    path('events/by-trip/<slug:trip_slug>/', get_trip_events, name='get_trip_events'),
    path('events/by-trip/<slug:trip_slug>/delete/', delete_trip_events, name='delete_trip_events'),
    
    # 特殊查询
    path('events/with-location/', get_events_with_location, name='get_events_with_location'),
    path('events/from-roamio/', get_roamio_events, name='get_roamio_events'),
    
    # 事件状态更新
    path('events/<int:event_id>/mark-notified/', mark_notification_sent, name='mark_notification_sent'),
]

