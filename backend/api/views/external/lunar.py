"""
Lunar Calendar API - 农历转换
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from lunarcalendar import Converter, Solar


@api_view(['GET'])
def get_lunar_date(request):
    """农历转换 API"""
    date_str = request.GET.get('date')  # 格式：2025-11-05
    
    if not date_str:
        return Response({'error': '请提供 date 参数'}, status=400)
    
    try:
        # 解析日期
        year, month, day = map(int, date_str.split('-'))
        
        # 转换为农历
        solar = Solar(year, month, day)
        lunar = Converter.Solar2Lunar(solar)
        
        # 生肖对照表
        zodiac_list = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        zodiac = zodiac_list[(lunar.year - 4) % 12]
        
        # 月份中文
        month_cn = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
        lunar_month = f"{month_cn[lunar.month - 1]}月"
        
        # 日期中文
        day_cn = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day = day_cn[lunar.day - 1]
        
        return Response({
            'lunar_date': f"农历{lunar.year}年{lunar_month}{lunar_day}",
            'year': lunar.year,
            'month': lunar_month,
            'day': lunar_day,
            'zodiac': zodiac,
            'solar_date': date_str
        })
    except ValueError as e:
        return Response({'error': f'日期格式错误: {str(e)}'}, status=400)
    except Exception as e:
        return Response({'error': f'转换失败: {str(e)}'}, status=500)

