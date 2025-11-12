"""
融合相关视图 - 支持 Roamio × Ralendar 跨项目功能
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from ..models import Event, QQUser
from ..serializers import EventSerializer

# 初始化 logger
logger = logging.getLogger('django')

@api_view(['POST'])
@authentication_classes([])  # 禁用全局认证，完全手动处理
@permission_classes([AllowAny])  # 允许任何人访问
def batch_create_events(request):
    """
    批量创建事件（用于 Roamio 同步）
    
    跨应用认证说明：
    - Roamio Token 中的 user_id 在 Ralendar 中不存在
    - 需要手动验证 Token 并通过 UnionID 匹配用户
    
    **POST** `/api/events/batch/`
    
    ### 请求体示例
    ```json
    {
        "source_app": "roamio",
        "source_id": "trip_123",
        "related_trip_slug": "yunnan-trip-2025",
        "events": [
            {
                "title": "抵达昆明",
                "start_time": "2025-11-15T10:00:00Z",
                "end_time": "2025-11-15T12:00:00Z",
                "location": "昆明长水国际机场",
                "latitude": 25.1019,
                "longitude": 102.9292,
                "description": "飞机 CA1234，提前2小时到达",
                "reminder_minutes": 120,
                "email_reminder": true
            }
        ]
    }
    ```
    
    ### 响应示例
    ```json
    {
        "success": true,
        "created_count": 1,
        "skipped_count": 0,
        "events": [...]
    }
    ```
    """
    # 1. 手动验证 Token
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(
            {'error': '缺少认证 Token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token_str = auth_header.split(' ')[1]
    
    try:
        token = AccessToken(token_str)
        roamio_user_id = token['user_id']
    except TokenError as e:
        return Response(
            {'error': f'Token 无效: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # 2. 三层用户匹配逻辑（优先级递减）
    # 方案 A: 从请求中获取 unionid 和 openid
    unionid = request.data.get('unionid', '')
    openid = request.data.get('openid', '')
    
    # 方案 B: 从 Token payload 中获取
    if not unionid:
        unionid = token.payload.get('unionid', '')
    if not openid:
        openid = token.payload.get('openid', '')
    
    ralendar_user = None
    
    # ============ 第1层：UnionID 匹配（最优先）============
    if unionid:
        logger.info(f"[Fusion API] 🔍 尝试 UnionID 匹配: {unionid[:20]}...")
        qq_user = QQUser.objects.filter(unionid=unionid).first()
        
        if qq_user:
            ralendar_user = qq_user.user
            logger.info(f"[Fusion API] ✅ 通过 UnionID 匹配成功: {ralendar_user.username} (ID: {ralendar_user.id})")
    
    # ============ 第2层：OpenID 匹配（回退方案）============
    if not ralendar_user and openid:
        logger.info(f"[Fusion API] 🔍 UnionID 失败，尝试 OpenID 匹配: {openid[:20]}...")
        qq_user = QQUser.objects.filter(openid=openid).first()
        
        if qq_user:
            ralendar_user = qq_user.user
            logger.info(f"[Fusion API] ✅ 通过 OpenID 匹配成功: {ralendar_user.username} (ID: {ralendar_user.id})")
    
    # ============ 第3层：user_id 匹配（兼容方案）============
    if not ralendar_user:
        logger.info(f"[Fusion API] 🔍 UnionID/OpenID 都失败，尝试 user_id 匹配: {roamio_user_id}")
        try:
            ralendar_user = User.objects.get(id=roamio_user_id)
            logger.info(f"[Fusion API] ✅ 通过 user_id 匹配成功: {ralendar_user.username}")
        except User.DoesNotExist:
            logger.warning(f"[Fusion API] ⚠️ user_id {roamio_user_id} 不存在")
    
    # ============ 最后：返回错误（不再使用 anonymous）============
    if not ralendar_user:
        logger.error(f"[Fusion API] ❌ 所有匹配方案都失败！")
        logger.error(f"  - UnionID: {unionid if unionid else 'None'}")
        logger.error(f"  - OpenID: {openid if openid else 'None'}")
        logger.error(f"  - user_id: {roamio_user_id}")
        return Response(
            {
                'error': '无法识别用户',
                'detail': '请先用 QQ 登录 Ralendar，或在 Roamio 的请求中包含 openid 字段',
                'required_fields': ['unionid (推荐)', 'openid (备选)']
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 3. 处理请求数据
    data = request.data
    
    # 调试日志
    logger.info(f"[Fusion API] 收到请求")
    logger.info(f"[Fusion API] 原始数据: {data}")
    logger.info(f"[Fusion API] Roamio user_id: {roamio_user_id}")
    logger.info(f"[Fusion API] Ralendar user: {ralendar_user.username} (ID: {ralendar_user.id})")
    
    # 兼容两种格式
    # 格式 1（正确）: {"events": [...]}
    # 格式 2（Roamio 当前使用）: {"title": "...", "start_time": "..."}
    if 'events' in data:
        # 标准格式：批量创建
        source_app = data.get('source_app', 'roamio')
        source_id = data.get('source_id', '')
        related_trip_slug = data.get('related_trip_slug', '')
        events_data = data.get('events', [])
    else:
        # Roamio 格式：单个事件，包装成数组
        source_app = 'roamio'
        source_id = ''
        related_trip_slug = data.get('trip_slug', '')
        events_data = [data]  # 包装成数组
        logger.info(f"[Fusion API] 自动包装为数组格式")
    
    logger.info(f"[Fusion API] Events count: {len(events_data)}")
    logger.info(f"[Fusion API] Events data: {events_data[:2] if len(events_data) > 2 else events_data}")
    
    if not events_data:
        return Response(
            {'error': '事件列表不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_events = []
    errors = []
    
    for idx, event_data in enumerate(events_data):
        try:
            # 合并来源信息
            event_data['source_app'] = source_app
            event_data['source_id'] = source_id
            event_data['related_trip_slug'] = related_trip_slug
            
            # 序列化并保存（在 save() 时传递 user 对象）
            serializer = EventSerializer(data=event_data)
            if serializer.is_valid():
                event = serializer.save(user=ralendar_user)  # ← 关键！传递 user 对象
                logger.info(f"[Fusion API] ✅ 创建成功: {event.title} (ID: {event.id})")
                created_events.append(event)
                
                # 如果需要邮件提醒，标记（实际发送需要异步任务）
                if event_data.get('email_reminder'):
                    # TODO: 添加到邮件提醒任务队列
                    pass
            else:
                errors.append({
                    'index': idx,
                    'title': event_data.get('title', 'Unknown'),
                    'errors': serializer.errors
                })
        except Exception as e:
            errors.append({
                'index': idx,
                'title': event_data.get('title', 'Unknown'),
                'error': str(e)
            })
    
    # 序列化返回
    result_serializer = EventSerializer(created_events, many=True)
    
    response_data = {
        'success': True,
        'created_count': len(created_events),
        'skipped_count': len(errors),
        'events': result_serializer.data
    }
    
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([])  # 手动处理认证
@permission_classes([AllowAny])
def get_user_events(request):
    """
    获取用户的所有事件（支持 UnionID 跨应用认证）
    
    **GET** `/api/v1/fusion/events/`
    
    ### 请求头
    ```
    Authorization: Bearer <roamio_token>
    ```
    
    ### 可选参数
    - unionid: QQ UnionID（推荐）
    - openid: QQ OpenID（备选）
    
    ### 响应示例
    ```json
    {
        "user_id": 2,
        "username": "W ૧ H",
        "events_count": 10,
        "events": [...]
    }
    ```
    """
    # 1. 手动验证 Token（复用 batch_create_events 的逻辑）
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response(
            {'error': '缺少认证 Token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token_str = auth_header.split(' ')[1]
    
    try:
        token = AccessToken(token_str)
        roamio_user_id = token['user_id']
    except TokenError as e:
        return Response(
            {'error': f'Token 无效: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # 2. 三层用户匹配（复用 batch_create_events 的逻辑）
    unionid = request.GET.get('unionid', '') or token.payload.get('unionid', '')
    openid = request.GET.get('openid', '') or token.payload.get('openid', '')
    
    ralendar_user = None
    
    # 第1层：UnionID
    if unionid:
        logger.info(f"[Fusion API - GET] 🔍 UnionID 匹配: {unionid[:20]}...")
        qq_user = QQUser.objects.filter(unionid=unionid).first()
        if qq_user:
            ralendar_user = qq_user.user
            logger.info(f"[Fusion API - GET] ✅ UnionID 匹配成功: {ralendar_user.username}")
    
    # 第2层：OpenID
    if not ralendar_user and openid:
        logger.info(f"[Fusion API - GET] 🔍 OpenID 匹配: {openid[:20]}...")
        qq_user = QQUser.objects.filter(openid=openid).first()
        if qq_user:
            ralendar_user = qq_user.user
            logger.info(f"[Fusion API - GET] ✅ OpenID 匹配成功: {ralendar_user.username}")
    
    # 第3层：user_id
    if not ralendar_user:
        try:
            ralendar_user = User.objects.get(id=roamio_user_id)
            logger.info(f"[Fusion API - GET] ✅ user_id 匹配成功: {ralendar_user.username}")
        except User.DoesNotExist:
            pass
    
    if not ralendar_user:
        return Response(
            {'error': '无法识别用户', 'detail': '请提供 unionid 或 openid'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 3. 获取用户的所有事件
    events = Event.objects.filter(user=ralendar_user).order_by('-start_time')
    serializer = EventSerializer(events, many=True)
    
    return Response({
        'user_id': ralendar_user.id,
        'username': ralendar_user.username,
        'events_count': events.count(),
        'events': serializer.data
    })


@api_view(['GET', 'PUT', 'DELETE'])  # One function handles all methods!
@authentication_classes([])
@permission_classes([AllowAny])
def manage_event(request, event_id):
    """
    Manage single event (RESTful with UnionID support)
    
    **GET**    `/api/v1/fusion/events/{id}/` - Get event detail
    **PUT**    `/api/v1/fusion/events/{id}/` - Update event
    **DELETE** `/api/v1/fusion/events/{id}/` - Delete event
    
    ### Headers
    ```
    Authorization: Bearer <roamio_token>
    ```
    
    ### Request Body (PUT only)
    ```json
    {
        "unionid": "UID_xxx...",
        "title": "New Title",
        "start_time": "2025-11-10T10:00:00Z"
    }
    ```
    """
    # Token 验证 + 三层用户匹配（复用逻辑）
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': '缺少认证 Token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token_str = auth_header.split(' ')[1]
    try:
        token = AccessToken(token_str)
        roamio_user_id = token['user_id']
    except TokenError as e:
        return Response({'error': f'Token 无效: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # 三层匹配（支持 URL 参数和请求体）
    unionid = request.GET.get('unionid', '') or request.data.get('unionid', '') or token.payload.get('unionid', '')
    openid = request.GET.get('openid', '') or request.data.get('openid', '') or token.payload.get('openid', '')
    
    ralendar_user = None
    if unionid:
        qq_user = QQUser.objects.filter(unionid=unionid).first()
        if qq_user:
            ralendar_user = qq_user.user
    if not ralendar_user and openid:
        qq_user = QQUser.objects.filter(openid=openid).first()
        if qq_user:
            ralendar_user = qq_user.user
    if not ralendar_user:
        try:
            ralendar_user = User.objects.get(id=roamio_user_id)
        except User.DoesNotExist:
            pass
    
    if not ralendar_user:
        return Response({'error': '无法识别用户'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find event and verify ownership
    try:
        event = Event.objects.get(id=event_id, user=ralendar_user)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found or no permission'}, status=status.HTTP_404_NOT_FOUND)
    
    # RESTful: handle different methods
    if request.method == 'GET':
        # Get event detail
        serializer = EventSerializer(event)
        logger.info(f"[Fusion API - GET] Get event {event_id}: {event.title}")
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Update event
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[Fusion API - PUT] Update event {event_id}: {event.title}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Delete event
        event_title = event.title
        event.delete()
        logger.info(f"[Fusion API - DELETE] Delete event {event_id}: {event_title}")
        return Response({
            'success': True,
            'message': f'Event "{event_title}" deleted'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_events(request, trip_slug):
    """
    获取旅行计划关联的所有事件
    
    **GET** `/api/events/by-trip/{trip_slug}/`
    
    ### 响应示例
    ```json
    {
        "trip_slug": "yunnan-trip-2025",
        "events_count": 5,
        "events": [...]
    }
    ```
    """
    events = Event.objects.filter(
        user=request.user,
        related_trip_slug=trip_slug
    ).order_by('start_time')
    
    serializer = EventSerializer(events, many=True)
    
    return Response({
        'trip_slug': trip_slug,
        'events_count': events.count(),
        'events': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_trip_events(request, trip_slug):
    """
    删除旅行计划关联的所有事件
    
    **DELETE** `/api/events/by-trip/{trip_slug}/`
    
    ### 响应示例
    ```json
    {
        "success": true,
        "deleted_count": 5,
        "message": "已删除 5 个关联事件"
    }
    ```
    """
    events = Event.objects.filter(
        user=request.user,
        related_trip_slug=trip_slug
    )
    
    deleted_count = events.count()
    events.delete()
    
    return Response({
        'success': True,
        'deleted_count': deleted_count,
        'message': f'已删除 {deleted_count} 个关联事件'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_sent(request, event_id):
    """
    标记事件提醒已发送
    
    **POST** `/api/events/{id}/mark-notified/`
    
    ### 响应示例
    ```json
    {
        "success": true,
        "message": "已标记为已发送"
    }
    ```
    """
    try:
        event = Event.objects.get(id=event_id, user=request.user)
        event.notification_sent = True
        event.save(update_fields=['notification_sent'])
        
        return Response({
            'success': True,
            'message': '已标记为已发送'
        })
    except Event.DoesNotExist:
        return Response(
            {'error': '事件不存在或无权访问'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_events_with_location(request):
    """
    获取所有有地理位置的事件（用于地图视图）
    
    **GET** `/api/events/with-location/`
    
    ### 查询参数
    - `map_provider`: 可选，筛选地图服务商 (baidu/amap/tencent)
    
    ### 响应示例
    ```json
    {
        "count": 10,
        "events": [...]
    }
    ```
    """
    events = Event.objects.filter(
        user=request.user,
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-start_time')
    
    # 可选：按地图服务商筛选
    map_provider = request.query_params.get('map_provider')
    if map_provider:
        events = events.filter(map_provider=map_provider)
    
    serializer = EventSerializer(events, many=True)
    
    return Response({
        'count': events.count(),
        'events': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_roamio_events(request):
    """
    获取所有来自 Roamio 的事件
    
    **GET** `/api/events/from-roamio/`
    
    ### 响应示例
    ```json
    {
        "count": 5,
        "events": [...]
    }
    ```
    """
    events = Event.objects.filter(
        user=request.user,
        source_app='roamio'
    ).order_by('-start_time')
    
    serializer = EventSerializer(events, many=True)
    
    return Response({
        'count': events.count(),
        'events': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_from_roamio(request):
    """
    从 Roamio 同步旅行计划到日历
    
    **POST** `/api/sync/from-roamio/`
    
    ### 请求体示例
    ```json
    {
        "trip_slug": "yunnan-trip-2025",
        "trip_title": "云南秘境探索",
        "itinerary": [
            {
                "day": 1,
                "date": "2025-11-15",
                "activities": [
                    {
                        "time": "10:00",
                        "title": "抵达昆明",
                        "location": "昆明长水国际机场",
                        "latitude": 25.1019,
                        "longitude": 102.9292
                    }
                ]
            }
        ]
    }
    ```
    
    ### 响应示例
    ```json
    {
        "success": true,
        "synced_count": 8,
        "events": [...]
    }
    ```
    """
    data = request.data
    trip_slug = data.get('trip_slug')
    trip_title = data.get('trip_title', '')
    itinerary = data.get('itinerary', [])
    
    if not trip_slug or not itinerary:
        return Response(
            {'error': '缺少必要参数：trip_slug 和 itinerary'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 先检查是否已经同步过（避免重复）
    existing_count = Event.objects.filter(
        user=request.user,
        related_trip_slug=trip_slug
    ).count()
    
    if existing_count > 0:
        return Response(
            {
                'error': f'该旅行计划已同步过（存在 {existing_count} 个事件）',
                'tip': '如需重新同步，请先删除已有事件'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 提取事件并创建
    events_to_create = []
    
    for day_item in itinerary:
        date = day_item.get('date')
        activities = day_item.get('activities', [])
        
        for activity in activities:
            time_str = activity.get('time', '09:00')
            start_time = f"{date}T{time_str}:00Z"
            
            event_data = {
                'user': request.user.id,
                'title': f"{trip_title} - {activity.get('title', '')}",
                'description': activity.get('description', ''),
                'start_time': start_time,
                'location': activity.get('location', ''),
                'latitude': activity.get('latitude'),
                'longitude': activity.get('longitude'),
                'source_app': 'roamio',
                'source_id': activity.get('id', ''),
                'related_trip_slug': trip_slug,
                'reminder_minutes': 60,  # 默认提前1小时
                'email_reminder': False
            }
            
            serializer = EventSerializer(data=event_data)
            if serializer.is_valid():
                event = serializer.save()
                events_to_create.append(event)
    
    # 返回创建的事件
    result_serializer = EventSerializer(events_to_create, many=True)
    
    return Response({
        'success': True,
        'synced_count': len(events_to_create),
        'events': result_serializer.data
    }, status=status.HTTP_201_CREATED)

