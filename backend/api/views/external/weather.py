"""
高德地图天气API视图

提供天气查询功能
"""

import logging
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_weather(request):
    """
    获取指定城市的实时天气（使用高德地图API）
    
    参数：
    - location: 城市名称（必填）
              例如：北京、上海、广州
    
    返回：
    - success: true/false
    - data: 天气数据
      - location: 城市名称
      - temperature: 温度（℃）
      - weather: 天气状况（如：晴、多云、阴）
      - windDir: 风向
      - windScale: 风力等级
      - humidity: 相对湿度（%）
      - feelsLike: 体感温度（℃，暂不支持）
      - updateTime: 更新时间
    """
    
    # 获取请求参数
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查API Key
    api_key = getattr(settings, 'AMAP_API_KEY', '')
    if not api_key:
        logger.error('高德地图API Key未配置')
        return Response({
            'success': False,
            'error': '天气服务未配置'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # 调用高德地图API - 实时天气
        url = 'https://restapi.amap.com/v3/weather/weatherInfo'
        params = {
            'city': location,  # 城市名称或adcode
            'key': api_key,  # API Key
            'extensions': 'base'  # 返回实况天气
        }
        
        logger.info(f'请求高德地图天气API: location={location}')
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f'高德地图API响应: status={data.get("status")}, info={data.get("info")}')
        
        # 检查API返回状态
        if data.get('status') != '1':
            error_msg = data.get('info', '未知错误')
            logger.error(f'高德地图API错误: {error_msg}')
            return Response({
                'success': False,
                'error': f'天气查询失败: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否有数据
        lives = data.get('lives', [])
        if not lives:
            logger.error(f'未找到城市天气数据: {location}')
            return Response({
                'success': False,
                'error': f'未找到城市: {location}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 提取天气数据（取第一个结果）
        live = lives[0]
        
        # 计算体感温度（简易公式）
        try:
            temp = float(live.get('temperature', 0))
            humidity = float(live.get('humidity', 50))
            # 简易体感温度公式：体感 = 实际温度 - (风速影响) + (湿度影响)
            # 高湿度会让体感更热/更冷
            humidity_effect = (humidity - 50) * 0.05  # 湿度偏离50%的影响
            feels_like = temp + humidity_effect
            feels_like_str = f"{int(round(feels_like))}"
        except (ValueError, TypeError):
            feels_like_str = live.get('temperature', '--')  # 降级使用实际温度
        
        weather_data = {
            'location': live.get('city', location),  # 城市名称
            'temperature': live.get('temperature', '--'),  # 温度
            'weather': live.get('weather', '未知'),  # 天气状况
            'windDir': live.get('winddirection', '--'),  # 风向
            'windScale': live.get('windpower', '--'),  # 风力等级
            'humidity': live.get('humidity', '--'),  # 相对湿度
            'feelsLike': feels_like_str,  # 计算的体感温度
            'updateTime': live.get('reporttime', '')  # 更新时间
        }
        
        logger.info(f'天气数据: {location} {weather_data["temperature"]}℃ {weather_data["weather"]}')
        
        return Response({
            'success': True,
            'data': weather_data
        })
        
    except requests.exceptions.Timeout:
        logger.error('高德地图API请求超时')
        return Response({
            'success': False,
            'error': '天气服务请求超时，请稍后重试'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    except requests.exceptions.RequestException as e:
        logger.error(f'高德地图API请求失败: {str(e)}')
        return Response({
            'success': False,
            'error': '无法连接到天气服务'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        logger.error(f'获取天气数据异常: {str(e)}', exc_info=True)
        return Response({
            'success': False,
            'error': '获取天气数据失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_location(request):
    """
    搜索城市（OpenWeatherMap不需要此功能，保留接口兼容性）
    
    参数：
    - location: 城市名称（必填）
    
    返回：
    - success: true/false
    - data: 直接返回输入的城市名
    """
    
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # OpenWeatherMap直接支持城市名查询，无需LocationID
    return Response({
        'success': True,
        'data': [{'name': location}]
    })

