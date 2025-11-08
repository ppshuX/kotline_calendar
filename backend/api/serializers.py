from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, PublicCalendar


# ==================== 用户相关 ====================
class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("两次密码不一致")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    photo = serializers.SerializerMethodField()
    acwing_openid = serializers.SerializerMethodField()
    qq_openid = serializers.SerializerMethodField()
    has_password = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'photo', 
                  'acwing_openid', 'qq_openid', 'has_password']
        read_only_fields = ['id', 'date_joined', 'photo', 'acwing_openid', 'qq_openid', 'has_password']
    
    def get_photo(self, obj):
        """获取用户头像（优先 AcWing，其次 QQ）"""
        if hasattr(obj, 'acwing_profile'):
            return obj.acwing_profile.photo_url
        elif hasattr(obj, 'qq_profile'):
            return obj.qq_profile.photo_url
        return None
    
    def get_acwing_openid(self, obj):
        """获取 AcWing OpenID（用于判断是否绑定）"""
        if hasattr(obj, 'acwing_profile'):
            return obj.acwing_profile.openid
        return None
    
    def get_qq_openid(self, obj):
        """获取 QQ OpenID（用于判断是否绑定）"""
        if hasattr(obj, 'qq_profile'):
            return obj.qq_profile.openid
        return None
    
    def get_has_password(self, obj):
        """判断用户是否设置了密码"""
        return obj.has_usable_password()


# ==================== 事件相关 ====================
class EventSerializer(serializers.ModelSerializer):
    """事件序列化器（融合版）"""
    username = serializers.CharField(source='user.username', read_only=True)
    map_url = serializers.CharField(read_only=True)
    has_location = serializers.BooleanField(read_only=True)
    is_from_roamio = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time', 'location',
            'reminder_minutes', 'username', 'created_at', 'updated_at',
            # 来源追踪字段
            'source_app', 'source_id', 'related_trip_slug',
            # 地图信息字段
            'latitude', 'longitude', 'map_provider', 'map_url', 'has_location',
            # 提醒配置字段
            'email_reminder', 'notification_sent',
            # 派生字段
            'is_from_roamio'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at', 
                            'map_url', 'has_location', 'is_from_roamio']
    
    def validate(self, data):
        """验证数据"""
        # 如果有经纬度，两者必须同时存在
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
            raise serializers.ValidationError("经纬度必须同时提供或同时为空")
        
        # 验证经纬度范围
        if latitude is not None:
            if not (-90 <= latitude <= 90):
                raise serializers.ValidationError("纬度必须在 -90 到 90 之间")
            if not (-180 <= longitude <= 180):
                raise serializers.ValidationError("经度必须在 -180 到 180 之间")
        
        return data


class PublicCalendarSerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = PublicCalendar
        fields = ['id', 'name', 'url_slug', 'description', 'is_public', 'events_count', 'created_at']
        read_only_fields = ['id', 'created_at']

