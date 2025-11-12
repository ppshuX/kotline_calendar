"""
AI助手 - 通义千问集成
"""
import json
import logging
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


def call_qwen_api(prompt: str, system_prompt: str = None) -> str:
    """
    调用通义千问API
    
    参数:
        prompt: 用户输入
        system_prompt: 系统提示词（可选）
    
    返回:
        AI响应文本
    """
    api_key = getattr(settings, 'QWEN_API_KEY', None)
    if not api_key:
        raise ValueError("未配置通义千问API密钥")
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    data = {
        "model": "qwen-turbo",  # 或 "qwen-plus", "qwen-max"
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 提取AI回复
        if result.get('output') and result['output'].get('choices'):
            return result['output']['choices'][0]['message']['content']
        else:
            logger.error(f"通义千问API响应格式异常: {result}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"调用通义千问API失败: {e}")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parse_event_from_text(request):
    """
    解析自然语言输入为日程事件
    
    POST /api/ai/parse-event/
    {
        "text": "明天下午3点开会，讨论项目方案"
    }
    
    响应:
    {
        "title": "项目方案讨论会议",
        "date": "2025-11-13",
        "time": "15:00",
        "description": "讨论项目方案",
        "reminder_minutes": 15
    }
    """
    text = request.data.get('text')
    if not text:
        return Response({'error': '请提供文本输入'}, status=400)
    
    # 构建系统提示词
    system_prompt = """你是一个日程助手，负责将用户的自然语言输入解析为结构化的日程信息。

当前日期时间: {now}

请将用户输入解析为JSON格式，包含以下字段：
- title: 日程标题（必填）
- date: 日期 YYYY-MM-DD 格式（必填）
- time: 时间 HH:MM 格式（可选，没有时间信息则不填）
- description: 描述（可选）
- reminder_minutes: 提前提醒分钟数（可选，默认15分钟）

注意：
1. "明天"、"后天"等相对时间要转换为具体日期
2. "下午3点"要转换为24小时制"15:00"
3. 如果没有明确时间，可以根据事件类型推荐时间
4. 只返回JSON，不要其他文字

示例：
输入: "明天下午3点开会，讨论项目方案"
输出: {{"title": "项目方案讨论会议", "date": "2025-11-13", "time": "15:00", "description": "讨论项目方案", "reminder_minutes": 15}}
""".format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        # 调用AI
        ai_response = call_qwen_api(text, system_prompt)
        
        if not ai_response:
            return Response({'error': 'AI解析失败'}, status=500)
        
        # 解析JSON
        try:
            # 尝试从AI响应中提取JSON
            ai_response = ai_response.strip()
            if ai_response.startswith('```json'):
                ai_response = ai_response[7:]
            if ai_response.endswith('```'):
                ai_response = ai_response[:-3]
            ai_response = ai_response.strip()
            
            event_data = json.loads(ai_response)
            
            # 验证必填字段
            if 'title' not in event_data or 'date' not in event_data:
                return Response({
                    'error': 'AI解析结果缺少必填字段',
                    'raw_response': ai_response
                }, status=500)
            
            return Response({
                'success': True,
                'event': event_data,
                'raw_response': ai_response
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"解析AI响应JSON失败: {e}, 原始响应: {ai_response}")
            return Response({
                'error': 'AI返回格式错误',
                'raw_response': ai_response
            }, status=500)
            
    except Exception as e:
        logger.error(f"AI解析日程失败: {e}")
        return Response({'error': f'处理失败: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def summarize_schedule(request):
    """
    智能总结日程
    
    POST /api/ai/summarize/
    {
        "events": [
            {"title": "会议A", "dateTime": "2025-11-13T10:00:00"},
            {"title": "会议B", "dateTime": "2025-11-13T15:00:00"}
        ],
        "date_range": "today"  // "today", "week", "month"
    }
    
    响应:
    {
        "summary": "今天有2个会议..."
    }
    """
    events = request.data.get('events', [])
    date_range = request.data.get('date_range', 'today')
    
    if not events:
        return Response({
            'summary': '当前时间段没有日程安排。'
        })
    
    # 构建提示词
    events_text = "\n".join([
        f"- {e.get('title', '无标题')} ({e.get('dateTime', '未知时间')})"
        for e in events
    ])
    
    range_text = {
        'today': '今天',
        'week': '本周',
        'month': '本月'
    }.get(date_range, '当前')
    
    system_prompt = """你是一个日程助手，负责总结用户的日程安排。

请用简洁、友好的语言总结用户的日程，包括：
1. 日程数量和类型统计
2. 重点提醒（时间紧张、重要事项等）
3. 时间安排建议（如果有空闲时间）

要求：
- 语言简洁明了
- 使用emoji增加可读性
- 不超过200字
"""
    
    prompt = f"请总结{range_text}的日程安排：\n\n{events_text}"
    
    try:
        ai_response = call_qwen_api(prompt, system_prompt)
        
        return Response({
            'success': True,
            'summary': ai_response or '总结生成失败'
        })
        
    except Exception as e:
        logger.error(f"AI总结日程失败: {e}")
        return Response({'error': f'处理失败: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    """
    对话式日程管理
    
    POST /api/ai/chat/
    {
        "message": "帮我看看下周有什么安排？",
        "context": {
            "current_date": "2025-11-12",
            "events": [...]
        }
    }
    
    响应:
    {
        "reply": "下周您有3个安排..."
    }
    """
    message = request.data.get('message')
    context = request.data.get('context', {})
    
    if not message:
        return Response({'error': '请提供消息内容'}, status=400)
    
    # 构建上下文
    events_summary = ""
    if context.get('events'):
        events_summary = "\n用户的日程：\n" + "\n".join([
            f"- {e.get('title')} ({e.get('dateTime')})"
            for e in context.get('events', [])[:10]  # 最多10条
        ])
    
    system_prompt = f"""你是一个智能日程助手，帮助用户管理日程。

当前日期: {context.get('current_date', datetime.now().strftime('%Y-%m-%d'))}
{events_summary}

你的职责：
1. 回答用户关于日程的问题
2. 帮助用户创建、修改日程
3. 提供时间管理建议
4. 检测日程冲突

回复要求：
- 简洁友好
- 使用emoji
- 如果需要创建日程，询问更多细节
"""
    
    try:
        ai_response = call_qwen_api(message, system_prompt)
        
        return Response({
            'success': True,
            'reply': ai_response or '抱歉，我没有理解您的问题。'
        })
        
    except Exception as e:
        logger.error(f"AI对话失败: {e}")
        return Response({'error': f'处理失败: {str(e)}'}, status=500)

