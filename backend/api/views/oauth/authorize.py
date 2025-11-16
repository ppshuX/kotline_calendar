"""
OAuth 2.0 授权端点
实现标准的 Authorization Code Flow
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
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
        # 对于普通用户显示友好的错误页；对第三方应用返回标准 400
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'oauth/error.html',
                {
                    'title': '授权请求无效',
                    'message': '当前授权链接缺少必要参数，无法继续。',
                    'detail': '缺少必需参数：client_id、redirect_uri、response_type。'
                },
                status=400,
            )
        return HttpResponse('invalid_request: missing client_id / redirect_uri / response_type', status=400)
    
    if response_type != 'code':
        logger.warning(f"[OAuth] Unsupported response_type: {response_type}")
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'oauth/error.html',
                {
                    'title': '不支持的授权类型',
                    'message': '当前授权请求的 response_type 不被支持。',
                    'detail': f'仅支持 response_type=code，当前为：{response_type}。'
                },
                status=400,
            )
        return HttpResponse(f'unsupported_response_type: {response_type}', status=400)
    
    # 验证客户端
    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        logger.warning(f"[OAuth] Invalid client_id: {client_id}")
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'oauth/error.html',
                {
                    'title': '客户端标识无效',
                    'message': '无法识别发起授权请求的客户端应用。',
                    'detail': '请从合法的第三方应用（例如 Roamio）中重新点击“连接 Ralendar”。'
                },
                status=400,
            )
        return HttpResponse('invalid_client: client_id not found', status=400)
    
    # 验证 redirect_uri
    if not client.is_redirect_uri_allowed(redirect_uri):
        logger.warning(f"[OAuth] Invalid redirect_uri: {redirect_uri} for client {client.client_name}")
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'oauth/error.html',
                {
                    'title': '回调地址未被允许',
                    'message': '当前授权请求的回调地址未在应用白名单中。',
                    'detail': '请联系第三方应用开发者，确认其在 Ralendar 中配置了正确的 redirect_uri。'
                },
                status=400,
            )
        return HttpResponse('invalid_redirect_uri', status=400)
    
    # 验证 scope
    if not client.is_scope_allowed(scope):
        logger.warning(f"[OAuth] Invalid scope: {scope} for client {client.client_name}")
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'oauth/error.html',
                {
                    'title': '权限请求不被允许',
                    'message': '该应用请求的权限超出了为其配置的范围。',
                    'detail': '请联系第三方应用开发者，确认其在 Ralendar 中申请了正确的 scope。'
                },
                status=400,
            )
        return HttpResponse('invalid_scope', status=400)
    
    # GET 请求：显示授权页面
    if request.method == 'GET':
        from ...models import get_scope_description

        # 安全地获取 scope_descriptions
        try:
            scope_descriptions = get_scope_description(scope)
        except Exception as e:
            logger.error(f"[OAuth] Error getting scope descriptions: {str(e)}")
            scope_descriptions = ['读取日历', '读取用户信息']  # 默认值

        context = {
            'client': client,
            'client_name': client.client_name or '未知应用',
            'client_description': client.client_description or '',
            'logo_url': client.logo_url or '',
            'scope': scope,
            'scope_descriptions': scope_descriptions,
            'redirect_uri': redirect_uri,
            'state': state,
            'user': request.user if request.user.is_authenticated else None,
            'is_authenticated': request.user.is_authenticated,
            'next_url': request.get_full_path(),  # 授权完成后的回调URL（用于登录后重定向）
            # 确保所有参数都被传递给模板，用于表单隐藏字段
            'client_id_param': client_id,
            'redirect_uri_param': redirect_uri,
            'state_param': state,
            'scope_param': scope,
        }

        # 渲染模板（如果模板不存在，让 Django 抛出标准错误，避免自制复杂 HTML）
        return render(request, 'oauth/authorize.html', context)
    
    # POST 请求：处理授权决定
    if request.method == 'POST':
        # 必须登录
        if not request.user.is_authenticated:
            logger.warning(f"[OAuth] POST request without authentication")
            return HttpResponse('未登录', status=401)
        
        # 重新验证参数（优先从POST获取，如果没有则使用GET请求时的参数）
        # 这样即使表单提交时参数丢失，也能使用GET请求时的参数
        post_client_id = request.POST.get('client_id')
        post_redirect_uri = request.POST.get('redirect_uri')
        post_state = request.POST.get('state')
        post_scope = request.POST.get('scope')
        
        # 如果POST中没有参数，使用GET请求时的参数（函数开始时已经验证）
        client_id = post_client_id or client_id
        redirect_uri = post_redirect_uri or redirect_uri
        state = post_state or state
        scope = post_scope or scope
        
        # 验证必需参数
        if not all([client_id, redirect_uri]):
            logger.error(f"[OAuth] Missing required parameters. POST: client_id={post_client_id}, redirect_uri={post_redirect_uri}, GET: client_id={client_id}, redirect_uri={redirect_uri}")
            return HttpResponse('缺少必需参数: client_id, redirect_uri', status=400)
        
        # 重新获取客户端（防止client对象丢失或POST中的client_id与GET不同）
        try:
            client = OAuthClient.objects.get(client_id=client_id, is_active=True)
        except OAuthClient.DoesNotExist:
            logger.error(f"[OAuth] Invalid client_id: {client_id}")
            return HttpResponse(f'无效的 client_id: {client_id}', status=400)
        
        # 验证 redirect_uri
        if not client.is_redirect_uri_allowed(redirect_uri):
            logger.error(f"[OAuth] Invalid redirect_uri: {redirect_uri} for client {client.client_name}")
            return HttpResponse(f'redirect_uri 不在白名单内: {redirect_uri}', status=400)
        
        action = request.POST.get('action')
        logger.info(f"[OAuth] POST action: {action}, client: {client.client_name} ({client_id}), redirect_uri: {redirect_uri}, state: {state[:50] if state else 'None'}")
        
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
            
            # 确保 redirect_uri 是完整的 URL（必须以 http:// 或 https:// 开头）
            if not redirect_uri.startswith(('http://', 'https://')):
                logger.error(f"[OAuth] ❌ redirect_uri is not a complete URL: {redirect_uri}")
                return HttpResponse(
                    f'无效的 redirect_uri: {redirect_uri}（必须是完整的 URL，如 https://example.com/callback）',
                    status=400
                )
            
            redirect_url = f"{redirect_uri}?{urlencode(params)}"
            logger.info(f"[OAuth] User {request.user.id} authorized client {client.client_name}, redirecting to {redirect_uri}")
            
            # 使用 HttpResponseRedirect 确保重定向执行
            return HttpResponseRedirect(redirect_url)
        
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
            logger.info(f"[OAuth] User {request.user.id} denied authorization for client {client.client_name}, redirecting to {redirect_uri}")
            
            # 使用 HttpResponseRedirect 确保重定向执行
            return HttpResponseRedirect(redirect_url)
        
        else:
            logger.warning(f"[OAuth] Invalid action: {action}")
            return HttpResponse(f'无效的操作: {action}', status=400)

