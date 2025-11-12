"""
和风天气API视图

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
    获取指定城市的实时天气
    
    参数：
    - location: 城市名称或LocationID（必填）
              例如：北京、上海、101010100
    
    返回：
    - success: true/false
    - data: 天气数据
      - location: 城市名称
      - temperature: 温度（℃）
      - weather: 天气状况（如：晴、多云、阴）
      - windDir: 风向
      - windScale: 风力等级
      - humidity: 相对湿度（%）
      - feelsLike: 体感温度（℃）
      - updateTime: 更新时间
    """
    
    # 获取请求参数
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称或LocationID'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查API Key
    api_key = settings.QWEATHER_API_KEY
    if not api_key:
        logger.error('和风天气API Key未配置')
        return Response({
            'success': False,
            'error': '天气服务未配置'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # 调用和风天气API - 实时天气
        url = 'https://devapi.qweather.com/v7/weather/now'
        params = {
            'location': location,
            'key': api_key
        }
        
        # 添加请求头，模拟从网站请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://app7626.acapp.acwing.com.cn/',
            'Origin': 'https://app7626.acapp.acwing.com.cn'
        }
        
        logger.info(f'请求和风天气API: location={location}')
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f'和风天气API响应: code={data.get("code")}')
        
        # 检查API返回状态
        if data.get('code') != '200':
            error_msg = {
                '204': '请求成功但无数据',
                '400': '请求错误',
                '401': 'API Key无效',
                '402': '超过访问次数',
                '403': '无访问权限',
                '404': '数据不存在',
                '429': '超过限定的QPM',
                '500': '服务器错误'
            }.get(data.get('code'), f'未知错误 (code={data.get("code")})')
            
            logger.error(f'和风天气API错误: {error_msg}')
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 提取天气数据
        now = data.get('now', {})
        
        weather_data = {
            'location': location,  # 原始输入的城市
            'temperature': now.get('temp', '--'),  # 温度
            'weather': now.get('text', '未知'),  # 天气状况
            'windDir': now.get('windDir', '--'),  # 风向
            'windScale': now.get('windScale', '--'),  # 风力等级
            'humidity': now.get('humidity', '--'),  # 相对湿度
            'feelsLike': now.get('feelsLike', '--'),  # 体感温度
            'updateTime': now.get('obsTime', '')  # 更新时间
        }
        
        logger.info(f'天气数据: {location} {weather_data["temperature"]}℃ {weather_data["weather"]}')
        
        return Response({
            'success': True,
            'data': weather_data
        })
        
    except requests.exceptions.Timeout:
        logger.error('和风天气API请求超时')
        return Response({
            'success': False,
            'error': '天气服务请求超时，请稍后重试'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    except requests.exceptions.RequestException as e:
        logger.error(f'和风天气API请求失败: {str(e)}')
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
    搜索城市LocationID
    
    参数：
    - location: 城市名称（必填）
    
    返回：
    - success: true/false
    - data: 城市列表
      - id: LocationID
      - name: 城市名称
      - adm1: 省份
      - adm2: 市
      - country: 国家
    """
    
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    api_key = settings.QWEATHER_API_KEY
    if not api_key:
        return Response({
            'success': False,
            'error': '天气服务未配置'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # 调用和风天气API - 城市搜索
        url = 'https://geoapi.qweather.com/v2/city/lookup'
        params = {
            'location': location,
            'key': api_key
        }
        
        # 添加请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://app7626.acapp.acwing.com.cn/',
            'Origin': 'https://app7626.acapp.acwing.com.cn'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') != '200':
            return Response({
                'success': False,
                'error': '城市搜索失败'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 提取城市列表
        locations = []
        for loc in data.get('location', []):
            locations.append({
                'id': loc.get('id'),
                'name': loc.get('name'),
                'adm1': loc.get('adm1'),  # 省份
                'adm2': loc.get('adm2'),  # 市
                'country': loc.get('country')
            })
        
        return Response({
            'success': True,
            'data': locations
        })
        
    except Exception as e:
        logger.error(f'搜索城市异常: {str(e)}', exc_info=True)
        return Response({
            'success': False,
            'error': '搜索城市失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

