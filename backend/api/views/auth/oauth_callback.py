"""
OAuth2 Callback Handler - AcWing 授权回调接收
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def acwing_oauth_callback(request):
    """
    AcWing OAuth2 回调接收端点
    
    在 AcWing acapp 环境中，AcWingOS.api.oauth2.authorize 的 callback
    会接收这个端点返回的内容。必须返回纯 JSON 格式，不能是 HTML。
    """
    # 获取 URL 参数中的 code 和 state
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')
    
    # 返回纯 JSON 响应（不是 HTML）
    # AcWingOS 会将这个 JSON 对象传递给 callback 函数
    return JsonResponse({
        'code': code,
        'state': state
    })

