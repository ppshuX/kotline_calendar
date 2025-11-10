"""
Holidays API - 节假日信息
"""
import json
import os
from datetime import datetime, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache


# 节假日数据文件路径
HOLIDAYS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_holidays_data(year):
    """加载节假日数据"""
    cache_key = f'holidays_{year}'
    holidays = cache.get(cache_key)
    
    if holidays is None:
        file_path = os.path.join(HOLIDAYS_DATA_DIR, f'holidays_{year}.json')
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                holidays = json.load(f)
            # 缓存 24 小时
            cache.set(cache_key, holidays, 86400)
        else:
            holidays = {}
    
    return holidays


def get_holiday_info(target_date):
    """获取指定日期的节假日信息"""
    year = target_date.year
    holidays_data = load_holidays_data(year)
    
    if str(year) not in holidays_data:
        return None
    
    year_data = holidays_data[str(year)]
    date_str = target_date.strftime('%Y-%m-%d')
    
    # 检查是否是节假日
    holiday_info = {
        'is_holiday': False,
        'is_workday': False,
        'holiday_name': None,
        'holiday_type': None
    }
    
    # 检查主要节假日
    for holiday_name, holiday_date in year_data.items():
        if holiday_date == date_str:
            holiday_info['is_holiday'] = True
            holiday_info['holiday_name'] = holiday_name
            holiday_info['holiday_type'] = 'major'
            return holiday_info
    
    # 检查节假日假期
    for holiday_name, holiday_dates in year_data.items():
        if isinstance(holiday_dates, list) and date_str in holiday_dates:
            holiday_info['is_holiday'] = True
            # 提取节假日名称（去掉"假期"）
            holiday_info['holiday_name'] = holiday_name.replace('假期', '')
            holiday_info['holiday_type'] = 'vacation'
            return holiday_info
    
    return holiday_info


@api_view(['GET'])
@permission_classes([AllowAny])
def get_holidays(request):
    """获取指定年份的节假日列表"""
    year = request.GET.get('year', str(datetime.now().year))
    
    try:
        year = int(year)
        holidays_data = load_holidays_data(year)
        
        if str(year) not in holidays_data:
            return Response({
                'year': year,
                'holidays': [],
                'message': f'{year}年节假日数据未找到'
            })
        
        year_data = holidays_data[str(year)]
        holidays_list = []
        
        # 整理节假日数据
        for holiday_name, holiday_date in year_data.items():
            if isinstance(holiday_date, str):
                # 单个日期
                holidays_list.append({
                    'name': holiday_name,
                    'date': holiday_date,
                    'type': 'major'
                })
            elif isinstance(holiday_date, list):
                # 假期日期范围
                holidays_list.append({
                    'name': holiday_name,
                    'dates': holiday_date,
                    'start_date': holiday_date[0],
                    'end_date': holiday_date[-1],
                    'type': 'vacation',
                    'days': len(holiday_date)
                })
        
        return Response({
            'year': year,
            'holidays': holidays_list
        })
    except ValueError:
        return Response({'error': '年份格式错误'}, status=400)
    except Exception as e:
        return Response({'error': f'获取节假日失败: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_holiday(request):
    """检查指定日期的节假日（包括法定、国际、传统节日）"""
    date_str = request.GET.get('date')
    
    if not date_str:
        # 如果没有提供日期，使用今天
        target_date = date.today()
    else:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}, status=400)
    
    # 获取法定节假日信息
    holiday_info = get_holiday_info(target_date)
    
    # 构建完整的节日信息（和 get_today_holidays 一样的结构）
    result = {
        'date': target_date.strftime('%Y-%m-%d'),
        'holiday': holiday_info if holiday_info and holiday_info['is_holiday'] else None,
        'traditional_festivals': [],
        'international_festivals': []
    }
    
    # 检查国际节日和传统节日（复用 get_today_holidays 的逻辑）
    month_day = target_date.strftime('%m-%d')
    
    # 国际节日字典（带Emoji）
    international_festivals_dict = {
        '01-01': {'name': '元旦', 'emoji': '🎊'},
        '02-14': {'name': '情人节', 'emoji': '💕'},
        '03-08': {'name': '国际妇女节', 'emoji': '👩'},
        '03-12': {'name': '植树节', 'emoji': '🌳'},
        '04-01': {'name': '愚人节', 'emoji': '🤡'},
        '05-01': {'name': '国际劳动节', 'emoji': '💪'},
        '05-04': {'name': '青年节', 'emoji': '🎓'},
        '06-01': {'name': '国际儿童节', 'emoji': '🧒'},
        '07-01': {'name': '建党节', 'emoji': '🎉'},
        '08-01': {'name': '建军节', 'emoji': '🎖️'},
        '09-10': {'name': '教师节', 'emoji': '📚'},
        '10-01': {'name': '国庆节', 'emoji': '🇨🇳'},
        '11-11': {'name': '光棍节 / 双11购物节', 'emoji': '1️⃣'},
        '12-24': {'name': '平安夜', 'emoji': '🎄'},
        '12-25': {'name': '圣诞节', 'emoji': '🎅'}
    }
    
    # 传统节日（农历，2025年对应的公历日期）
    traditional_festivals_dict = {
        '01-28': {'name': '除夕', 'emoji': '🏮'},
        '01-29': {'name': '春节', 'emoji': '🧨'},
        '02-12': {'name': '元宵节', 'emoji': '🏮'},
        '05-31': {'name': '端午节', 'emoji': '🐉'},
        '10-06': {'name': '中秋节', 'emoji': '🥮'},
        '10-29': {'name': '重阳节', 'emoji': '🍵'}
    }
    
    # 添加国际节日（避免与法定节假日重复）
    if month_day in international_festivals_dict:
        festival = international_festivals_dict[month_day]
        # 如果已经有法定节假日，检查名称是否重复
        if not (result['holiday'] and result['holiday']['holiday_name'] == festival['name']):
            result['international_festivals'].append({
                'name': festival['name'],
                'emoji': festival['emoji'],
                'type': 'international'
            })
    
    # 添加传统节日（避免与法定节假日重复）
    if month_day in traditional_festivals_dict:
        festival = traditional_festivals_dict[month_day]
        # 如果已经有法定节假日，检查名称是否重复
        if not (result['holiday'] and result['holiday']['holiday_name'] == festival['name']):
            result['traditional_festivals'].append({
                'name': festival['name'],
                'emoji': festival['emoji'],
                'type': 'traditional'
            })
    
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_today_holidays(request):
    """获取今日节假日和节日信息"""
    today = date.today()
    
    # 获取节假日信息
    holiday_info = get_holiday_info(today)
    
    # 获取传统节日（农历）
    # 这里可以扩展，添加更多传统节日
    
    result = {
        'date': today.strftime('%Y-%m-%d'),
        'holiday': holiday_info if holiday_info and holiday_info['is_holiday'] else None,
        'traditional_festivals': [],
        'international_festivals': []
    }
    
    # 添加一些国际节日和特殊日子（可以根据日期判断）
    month_day = today.strftime('%m-%d')
    international_festivals = {
        '01-01': {'name': '元旦', 'emoji': '🎊'},
        '02-14': {'name': '情人节', 'emoji': '💕'},
        '03-08': {'name': '国际妇女节', 'emoji': '👩'},
        '03-12': {'name': '植树节', 'emoji': '🌳'},
        '04-01': {'name': '愚人节', 'emoji': '🤡'},
        '05-01': {'name': '国际劳动节', 'emoji': '💪'},
        '05-04': {'name': '青年节', 'emoji': '🎓'},
        '06-01': {'name': '国际儿童节', 'emoji': '🧒'},
        '07-01': {'name': '建党节', 'emoji': '🎉'},
        '08-01': {'name': '建军节', 'emoji': '🎖️'},
        '09-10': {'name': '教师节', 'emoji': '📚'},
        '10-01': {'name': '国庆节', 'emoji': '🇨🇳'},
        '11-11': {'name': '光棍节 / 双11购物节', 'emoji': '1️⃣'},
        '12-24': {'name': '平安夜', 'emoji': '🎄'},
        '12-25': {'name': '圣诞节', 'emoji': '🎅'}
    }
    
    if month_day in international_festivals:
        festival = international_festivals[month_day]
        result['international_festivals'].append({
            'name': festival['name'],
            'emoji': festival['emoji'],
            'type': 'international'
        })
    
    # 添加传统节日（农历节日，2025年对应的公历日期）
    traditional_festivals = {
        '01-28': {'name': '除夕', 'emoji': '🏮'},
        '01-29': {'name': '春节', 'emoji': '🧨'},
        '02-12': {'name': '元宵节', 'emoji': '🏮'},
        '05-31': {'name': '端午节', 'emoji': '🐉'},
        '10-06': {'name': '中秋节', 'emoji': '🥮'},
        '10-29': {'name': '重阳节', 'emoji': '🍵'}
    }
    
    if month_day in traditional_festivals:
        festival = traditional_festivals[month_day]
        result['traditional_festivals'].append({
            'name': festival['name'],
            'emoji': festival['emoji'],
            'type': 'traditional'
        })
    
    return Response(result)

