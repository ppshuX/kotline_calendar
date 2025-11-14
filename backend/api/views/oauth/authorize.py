"""
OAuth 2.0 授权端点
实现标准的 Authorization Code Flow
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from urllib.parse import urlencode, parse_qs, urlparse
import logging

from ...models import OAuthClient, AuthorizationCode

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def oauth_authorize(request):
    """
    OAuth 授权端点
    
    GET: 显示授权页面
    POST: 处理用户的授权决定
    
    URL: /oauth/authorize?client_id=xxx&redirect_uri=xxx&response_type=code&state=xxx&scope=xxx
    """
    
    # 获取参数
    client_id = request.GET.get('client_id') or request.POST.get('client_id')
    redirect_uri = request.GET.get('redirect_uri') or request.POST.get('redirect_uri')
    response_type = request.GET.get('response_type') or request.POST.get('response_type')
    state = request.GET.get('state') or request.POST.get('state', '')
    scope = request.GET.get('scope') or request.POST.get('scope', 'calendar:read user:read')
    
    # 参数验证
    if not all([client_id, redirect_uri, response_type]):
        logger.warning(f"[OAuth] Missing required parameters")
        return HttpResponse(
            '缺少必需参数: client_id, redirect_uri, response_type',
            status=400
        )
    
    if response_type != 'code':
        logger.warning(f"[OAuth] Unsupported response_type: {response_type}")
        return HttpResponse(
            f'不支持的 response_type: {response_type}，仅支持 "code"',
            status=400
        )
    
    # 验证客户端
    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        logger.warning(f"[OAuth] Invalid client_id: {client_id}")
        return HttpResponse(
            f'无效的 client_id: {client_id}',
            status=400
        )
    
    # 验证 redirect_uri
    if not client.is_redirect_uri_allowed(redirect_uri):
        logger.warning(f"[OAuth] Invalid redirect_uri: {redirect_uri} for client {client.client_name}")
        return HttpResponse(
            f'redirect_uri 不在白名单内: {redirect_uri}',
            status=400
        )
    
    # 验证 scope
    if not client.is_scope_allowed(scope):
        logger.warning(f"[OAuth] Invalid scope: {scope} for client {client.client_name}")
        return HttpResponse(
            f'请求的权限范围超出允许范围: {scope}',
            status=400
        )
    
    # GET 请求：显示授权页面
    if request.method == 'GET':
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            # 未登录，跳转到登录页面，登录后再回来
            login_url = f'/login?next={request.get_full_path()}'
            logger.info(f"[OAuth] User not authenticated, redirecting to login")
            return redirect(login_url)
        
        # 已登录，显示授权确认页面
        from ...models import get_scope_description
        
        context = {
            'client': client,
            'client_name': client.client_name,
            'client_description': client.client_description,
            'logo_url': client.logo_url,
            'scope': scope,
            'scope_descriptions': get_scope_description(scope),
            'redirect_uri': redirect_uri,
            'state': state,
            'user': request.user,
        }
        
        logger.info(f"[OAuth] Showing authorization page for user {request.user.id}, client {client.client_name}")
        return render(request, 'oauth/authorize.html', context)
    
    # POST 请求：处理授权决定
    if request.method == 'POST':
        # 必须登录
        if not request.user.is_authenticated:
            return HttpResponse('未登录', status=401)
        
        action = request.POST.get('action')
        
        if action == 'authorize':
            # 用户同意授权
            logger.info(f"[OAuth] User {request.user.id} authorized client {client.client_name}")
            
            # 生成授权码
            auth_code = AuthorizationCode.create_code(
                client=client,
                user=request.user,
                redirect_uri=redirect_uri,
                scope=scope,
                state=state
            )
            
            # 重定向回客户端（带授权码）
            params = {
                'code': auth_code.code,
            }
            if state:
                params['state'] = state
            
            redirect_url = f"{redirect_uri}?{urlencode(params)}"
            logger.info(f"[OAuth] Redirecting to {redirect_uri} with authorization code")
            return redirect(redirect_url)
        
        elif action == 'deny':
            # 用户拒绝授权
            logger.info(f"[OAuth] User {request.user.id} denied authorization for client {client.client_name}")
            
            # 重定向回客户端（带错误信息）
            params = {
                'error': 'access_denied',
                'error_description': '用户拒绝授权',
            }
            if state:
                params['state'] = state
            
            redirect_url = f"{redirect_uri}?{urlencode(params)}"
            logger.info(f"[OAuth] Redirecting to {redirect_uri} with access_denied error")
            return redirect(redirect_url)
        
        else:
            logger.warning(f"[OAuth] Invalid action: {action}")
            return HttpResponse(f'无效的操作: {action}', status=400)

