"""
运势相关视图
提供今日运势查询功能（结合天气、节气、黄历）
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
import requests
from django.conf import settings


# 二十四节气数据（2025年）
SOLAR_TERMS = {
    '01-05': {'name': '小寒', 'desc': '天气寒冷，宜养生保暖', 'boost': ['读书', '沐浴', '求医'], 'reduce': ['出行', '动土']},
    '01-20': {'name': '大寒', 'desc': '一年中最冷的时节', 'boost': ['祭祀', '祈福', '修造'], 'reduce': ['移徙', '嫁娶']},
    '02-03': {'name': '立春', 'desc': '春季开始，万物复苏', 'boost': ['开市', '求财', '纳财', '会友'], 'reduce': ['安葬', '破土']},
    '02-18': {'name': '雨水', 'desc': '降雨增多，气温回升', 'boost': ['栽种', '祈福', '开市'], 'reduce': ['动土', '修造']},
    '03-05': {'name': '惊蛰', 'desc': '春雷惊醒蛰伏', 'boost': ['出行', '交易', '求财', '会友'], 'reduce': ['安床', '移徙']},
    '03-20': {'name': '春分', 'desc': '昼夜平分，春意盎然', 'boost': ['嫁娶', '纳采', '祭祀'], 'reduce': ['诉讼', '词讼']},
    '04-04': {'name': '清明', 'desc': '天清地明，祭祖扫墓', 'boost': ['祭祀', '扫舍', '修墓'], 'reduce': ['嫁娶', '开市']},
    '04-20': {'name': '谷雨', 'desc': '雨生百谷，播种佳时', 'boost': ['栽种', '开市', '纳财'], 'reduce': ['移徙', '入宅']},
    '05-05': {'name': '立夏', 'desc': '夏季开始，气温升高', 'boost': ['出行', '会友', '交易'], 'reduce': ['动土', '破土']},
    '05-21': {'name': '小满', 'desc': '麦类作物籽粒饱满', 'boost': ['纳财', '开市', '求财'], 'reduce': ['诉讼', '安葬']},
    '06-05': {'name': '芒种', 'desc': '有芒作物成熟', 'boost': ['栽种', '纳财', '开市'], 'reduce': ['嫁娶', '移徙']},
    '06-21': {'name': '夏至', 'desc': '白昼最长，阳气最盛', 'boost': ['祈福', '求财', '交易'], 'reduce': ['词讼', '安葬']},
    '07-07': {'name': '小暑', 'desc': '天气炎热，注意防暑', 'boost': ['沐浴', '求医', '治病'], 'reduce': ['嫁娶', '移徙', '出行']},
    '07-22': {'name': '大暑', 'desc': '一年中最热的时节', 'boost': ['沐浴', '扫舍', '解除'], 'reduce': ['出行', '开市', '动土']},
    '08-07': {'name': '立秋', 'desc': '秋季开始，暑去凉来', 'boost': ['开市', '求财', '交易'], 'reduce': ['嫁娶', '移徙']},
    '08-23': {'name': '处暑', 'desc': '炎热结束，秋高气爽', 'boost': ['出行', '会友', '祭祀'], 'reduce': ['安葬', '破土']},
    '09-07': {'name': '白露', 'desc': '天气转凉，露水增多', 'boost': ['求医', '治病', '沐浴'], 'reduce': ['嫁娶', '移徙']},
    '09-23': {'name': '秋分', 'desc': '昼夜平分，丰收时节', 'boost': ['纳财', '开市', '祭祀'], 'reduce': ['诉讼', '词讼']},
    '10-08': {'name': '寒露', 'desc': '露水将凝，气温下降', 'boost': ['祈福', '祭祀', '求医'], 'reduce': ['嫁娶', '开市']},
    '10-23': {'name': '霜降', 'desc': '天气渐冷，初霜出现', 'boost': ['纳财', '开市', '修造'], 'reduce': ['移徙', '出行']},
    '11-07': {'name': '立冬', 'desc': '冬季开始，万物收藏', 'boost': ['祭祀', '修造', '纳财'], 'reduce': ['嫁娶', '移徙', '出行']},
    '11-22': {'name': '小雪', 'desc': '开始降雪，气温降低', 'boost': ['祭祀', '祈福', '修造'], 'reduce': ['嫁娶', '出行']},
    '12-07': {'name': '大雪', 'desc': '降雪增多，严寒将至', 'boost': ['修造', '祭祀', '沐浴'], 'reduce': ['嫁娶', '移徙', '出行']},
    '12-21': {'name': '冬至', 'desc': '阴极阳生，白昼最短', 'boost': ['祭祀', '祈福', '沐浴'], 'reduce': ['嫁娶', '移徙']}
}

# 黄历宜事列表
GOOD_THINGS_LIST = [
    "出行", "会友", "开市", "祈福", "求财", "纳财", "交易",
    "立券", "移徙", "嫁娶", "祭祀", "安床", "入宅", "动土",
    "修造", "纳采", "订盟", "理发", "求医", "治病", "沐浴",
    "扫舍", "裁衣", "作灶", "解除", "栽种", "牧养"
]

# 黄历忌事列表
BAD_THINGS_LIST = [
    "诉讼", "词讼", "动土", "破土", "安葬", "开市", "交易",
    "纳财", "栽种", "嫁娶", "移徙", "入宅", "安床", "作灶",
    "修造", "出行", "祈福", "祭祀", "探病", "针灸", "求医",
    "治病", "裁衣", "解除", "伐木", "捕捉", "畋猎"
]

# 幸运颜色列表
LUCKY_COLORS = [
    "红色", "橙色", "黄色", "绿色", "青色", "蓝色",
    "紫色", "粉色", "白色", "金色", "银色", "米色"
]

# 五行列表
ELEMENTS = ["金", "木", "水", "火", "土"]

# 运势描述列表
FORTUNE_DESCRIPTIONS = [
    "今日运势极佳，万事顺意！",
    "运势平稳，适宜稳扎稳打。",
    "小有波折，需谨慎行事。",
    "运势上扬，把握机会！",
    "诸事顺利，心情愉悦。",
    "运势一般，保持平常心。",
    "运势渐好，积极进取！"
]


def seeded_random_generator(seed):
    """基于种子的伪随机数生成器"""
    def random():
        nonlocal seed
        seed = (seed * 9301 + 49297) % 233280
        return seed / 233280
    return random


@api_view(['GET'])
@permission_classes([AllowAny])
def get_today_fortune(request):
    """
    获取今日运势
    
    **GET** `/api/fortune/today/`
    
    ### 查询参数
    - city: 城市名称（可选，用于获取天气数据）
    
    ### 响应示例
    ```json
    {
        "date": "2025-11-13",
        "weekday": "星期四",
        "solar_term": "立冬",
        "solar_term_desc": "冬季开始，万物收藏",
        "fortune_score": 85,
        "stars": 4,
        "star_display": "⭐⭐⭐⭐",
        "description": "今日立冬，冬季开始，万物收藏。",
        "good_things": ["祭祀", "修造", "纳财", "出行"],
        "bad_things": ["嫁娶", "移徙", "出行"],
        "lucky_color": "红色",
        "lucky_number": 8,
        "lucky_element": "火",
        "weekday_tip": "立冬：冬季开始，万物收藏。温度适宜，心情愉悦！😊",
        "weather": {
            "temperature": 17,
            "weather": "晴",
            "humidity": 62
        }
    }
    ```
    """
    # 获取今日日期
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    weekday_num = now.weekday()
    
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday = weekday_names[weekday_num]
    
    month_day = f"{month:02d}-{day:02d}"
    
    # 检查是否是节气
    solar_term_data = SOLAR_TERMS.get(month_day)
    solar_term = solar_term_data['name'] if solar_term_data else None
    solar_term_desc = solar_term_data['desc'] if solar_term_data else None
    
    # 获取天气数据（可选）
    city = request.GET.get('city', '南昌市')
    weather_data = None
    
    try:
        # 调用高德天气API
        amap_key = getattr(settings, 'AMAP_API_KEY', '')
        if amap_key:
            weather_url = f"https://restapi.amap.com/v3/weather/weatherInfo"
            weather_params = {
                'key': amap_key,
                'city': city,
                'extensions': 'base'
            }
            weather_response = requests.get(weather_url, params=weather_params, timeout=3)
            weather_result = weather_response.json()
            
            if weather_result.get('status') == '1' and weather_result.get('lives'):
                live = weather_result['lives'][0]
                weather_data = {
                    'temperature': int(live.get('temperature', 20)),
                    'weather': live.get('weather', '晴'),
                    'humidity': int(live.get('humidity', 60))
                }
    except Exception:
        pass
    
    # 生成运势数据
    fortune_data = generate_fortune(year, month, day, weekday_num, solar_term_data, weather_data)
    
    # 构造响应
    response_data = {
        'date': f"{year}-{month:02d}-{day:02d}",
        'weekday': weekday,
        'solar_term': solar_term,
        'solar_term_desc': solar_term_desc,
        **fortune_data
    }
    
    if weather_data:
        response_data['weather'] = weather_data
    
    return Response(response_data)


def generate_fortune(year, month, day, weekday_num, solar_term_data, weather_data):
    """
    生成运势数据（确定性算法）
    
    Args:
        year: 年份
        month: 月份
        day: 日期
        weekday_num: 星期几（0=周一，6=周日）
        solar_term_data: 节气数据
        weather_data: 天气数据
    
    Returns:
        dict: 运势数据
    """
    # 基于日期计算种子（确定性）
    seed = year * 10000 + month * 100 + day
    random = seeded_random_generator(seed)
    
    # 基础宜忌列表
    base_good_things = list(GOOD_THINGS_LIST)
    base_bad_things = list(BAD_THINGS_LIST)
    
    # 如果是节气，调整宜忌（节气优先）
    if solar_term_data:
        boost = solar_term_data.get('boost', [])
        reduce = solar_term_data.get('reduce', [])
        
        # 将节气推荐的事项提升到前面
        base_good_things = list(boost) + [item for item in base_good_things if item not in boost]
        # 将节气不推荐的事项提升到忌事前面
        base_bad_things = list(reduce) + [item for item in base_bad_things if item not in reduce]
    
    # 根据天气调整宜忌
    if weather_data:
        weather = weather_data.get('weather', '')
        temp = weather_data.get('temperature', 20)
        
        # 晴天
        if '晴' in weather:
            priority_good = ['出行', '会友', '祈福', '求财']
            base_good_things = priority_good + [item for item in base_good_things if item not in priority_good]
        # 雨天
        elif '雨' in weather:
            priority_good = ['读书', '沐浴', '扫舍', '修造']
            priority_bad = ['出行', '移徙', '嫁娶']
            base_good_things = priority_good + [item for item in base_good_things if item not in priority_good]
            base_bad_things = priority_bad + [item for item in base_bad_things if item not in priority_bad]
        # 雪天
        elif '雪' in weather:
            priority_good = ['祭祀', '祈福', '沐浴']
            priority_bad = ['出行', '嫁娶', '移徙', '开市']
            base_good_things = priority_good + [item for item in base_good_things if item not in priority_good]
            base_bad_things = priority_bad + [item for item in base_bad_things if item not in priority_bad]
        # 阴天/多云
        elif '阴' in weather or '云' in weather:
            priority_good = ['祭祀', '修造', '求医']
            base_good_things = priority_good + [item for item in base_good_things if item not in priority_good]
        
        # 高温（>30度）
        if temp > 30:
            priority_bad = ['出行', '开市', '移徙']
            base_bad_things = priority_bad + [item for item in base_bad_things if item not in priority_bad]
        # 低温（<5度）
        elif temp < 5:
            priority_bad = ['出行', '嫁娶', '移徙']
            base_bad_things = priority_bad + [item for item in base_bad_things if item not in priority_bad]
    
    # 随机选择宜忌
    good_count = 4 + int(random() * 4)  # 4-7项
    bad_count = 3 + int(random() * 3)   # 3-5项
    
    selected_good = set()
    selected_bad = set()
    
    # 选择宜事（优先从调整后的列表前面选择）
    for i in range(min(good_count, len(base_good_things))):
        selected_good.add(base_good_things[i])
    
    while len(selected_good) < good_count and len(base_good_things) > 0:
        idx = int(random() * len(base_good_things))
        selected_good.add(base_good_things[idx])
    
    # 选择忌事（优先从调整后的列表前面选择，且避免与宜事重复）
    for i in range(len(base_bad_things)):
        if len(selected_bad) >= bad_count:
            break
        if base_bad_things[i] not in selected_good:
            selected_bad.add(base_bad_things[i])
    
    while len(selected_bad) < bad_count and len(base_bad_things) > 0:
        idx = int(random() * len(base_bad_things))
        bad = base_bad_things[idx]
        if bad not in selected_good:
            selected_bad.add(bad)
    
    good_things = list(selected_good)
    bad_things = list(selected_bad)
    
    # 幸运元素
    lucky_color = LUCKY_COLORS[int(random() * len(LUCKY_COLORS))]
    lucky_number = int(random() * 100)
    lucky_element = ELEMENTS[int(random() * len(ELEMENTS))]
    
    # 基础运势分数
    base_score = 60 + int(random() * 40)  # 60-99分
    
    # 根据天气调整分数
    if weather_data:
        weather = weather_data.get('weather', '')
        temp = weather_data.get('temperature', 20)
        
        if '晴' in weather:
            base_score += 5  # 晴天加分
        elif '雨' in weather or '雪' in weather:
            base_score -= 3  # 雨雪天减分
        
        if 15 <= temp <= 25:
            base_score += 3  # 舒适温度加分
        elif temp > 35 or temp < 0:
            base_score -= 5  # 极端温度减分
    
    # 确保分数在60-99范围内
    fortune_score = max(60, min(99, base_score))
    
    # 根据节气、天气和分数生成运势描述
    if solar_term_data:
        description = f"今日{solar_term_data['name']}，{solar_term_data['desc']}。"
    elif weather_data:
        weather = weather_data.get('weather', '')
        if '晴' in weather:
            description = '天气晴朗，运势上扬，把握机会！'
        elif '雨' in weather:
            description = '雨天宜静养，适合思考和规划。'
        elif '雪' in weather:
            description = '雪天出行需谨慎，适合室内活动。'
        else:
            description = FORTUNE_DESCRIPTIONS[int(random() * len(FORTUNE_DESCRIPTIONS))]
    else:
        description = FORTUNE_DESCRIPTIONS[int(random() * len(FORTUNE_DESCRIPTIONS))]
    
    # 星级评分
    if fortune_score >= 90:
        stars = 5
        star_display = "⭐⭐⭐⭐⭐"
    elif fortune_score >= 80:
        stars = 4
        star_display = "⭐⭐⭐⭐"
    elif fortune_score >= 70:
        stars = 3
        star_display = "⭐⭐⭐"
    elif fortune_score >= 60:
        stars = 2
        star_display = "⭐⭐"
    else:
        stars = 1
        star_display = "⭐"
    
    # 温馨提示（结合天气）
    tip = ''
    
    if weather_data:
        weather = weather_data.get('weather', '')
        temp = weather_data.get('temperature', 20)
        
        # 基于天气的提示
        if '雨' in weather:
            tip = '今日有雨，出门记得带伞哦！☔ '
        elif '雪' in weather:
            tip = '今日下雪，注意保暖防滑！❄️ '
        elif '晴' in weather:
            tip = '今日晴朗，适合户外活动！☀️ '
        elif '雾' in weather or '霾' in weather:
            tip = '今日有雾霾，减少外出，注意健康！😷 '
        
        # 基于温度的提示
        if temp > 30:
            tip += '高温天气，多补充水分！🥤'
        elif temp < 5:
            tip += '寒冷天气，注意保暖！🧣'
        elif 15 <= temp <= 25:
            tip += '温度适宜，心情愉悦！😊'
    
    # 如果没有天气数据，使用星期提示
    if not tip:
        tips = [
            "周一元气满满！新的一周，加油开始！💪",
            "保持节奏，稳步前进！🚀",
            "周三已过半，坚持就是胜利！🌟",
            "临近周末，再努力一把！💫",
            "愉快的周五，周末即将到来！🎉",
            "周末愉快，享受休闲时光！🌈",
            "周日放松，为新的一周充电！⚡"
        ]
        tip = tips[weekday_num]
    
    # 如果是节气，添加节气提示
    if solar_term_data:
        tip = f"{solar_term_data['name']}：{solar_term_data['desc']}。{tip}"
    
    return {
        'fortune_score': fortune_score,
        'stars': stars,
        'star_display': star_display,
        'description': description,
        'good_things': good_things,
        'bad_things': bad_things,
        'lucky_color': lucky_color,
        'lucky_number': lucky_number,
        'lucky_element': lucky_element,
        'weekday_tip': tip
    }

