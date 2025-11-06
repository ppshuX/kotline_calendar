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
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


# ==================== 事件相关 ====================
class EventSerializer(serializers.ModelSerializer):
    """事件序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'location', 
                  'username', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']


class PublicCalendarSerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = PublicCalendar
        fields = ['id', 'name', 'url_slug', 'description', 'is_public', 'events_count', 'created_at']
        read_only_fields = ['id', 'created_at']

