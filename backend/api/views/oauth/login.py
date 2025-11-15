"""
OAuth 授权页面的登录处理
用于在OAuth授权流程中的登录
"""
from django.shortcuts import redirect
from django.contrib.auth import login as django_login
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import requests
import logging

from django.contrib.auth.models import User
from ...models import AcWingUser, QQUser

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
def oauth_web_login(request):
    """
    OAuth授权页面的登录处理
    用于在OAuth授权流程中，用户未登录时跳转到登录页面
    
    URL: /oauth/login?provider=acwing&next=/oauth/authorize?...
    或: /oauth/login?provider=qq&next=/oauth/authorize?...
    """
    from django.conf import settings
    
    provider = request.GET.get('provider', 'acwing')  # acwing 或 qq
    next_url = request.GET.get('next', '/oauth/authorize')
    
    if provider == 'acwing':
        # AcWing登录：重定向到AcWing授权页面
        ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/oauth/login/callback/acwing/"
        
        # 将 next_url 存储在 session 中，以便登录成功后重定向
        request.session['oauth_next_url'] = next_url
        
        auth_url = (
            f"https://www.acwing.com/third_party/api/oauth2/web/authorize/"
            f"?appid={ACWING_APPID}&redirect_uri={REDIRECT_URI}&scope=userinfo"
        )
        logger.info(f"[OAuth Login] Redirecting to AcWing auth: {auth_url}")
        return redirect(auth_url)
    
    elif provider == 'qq':
        # QQ登录：重定向到QQ授权页面
        QQ_APPID = getattr(settings, 'QQ_APPID', '')
        # 注意：QQ开放平台只能配置一个回调地址，统一使用 /qq/callback
        # 这与普通QQ登录保持一致，避免需要配置多个回调地址
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/qq/callback"
        
        # 将 next_url 存储在 session 中（用于回调后重定向）
        request.session['oauth_next_url'] = next_url
        logger.info(f"[OAuth Login] Storing next_url in session: {next_url}")
        
        # 同时将 next_url 编码到 state 参数中，防止 session 丢失
        # QQ的 state 参数可以传递自定义数据
        import base64
        import urllib.parse
        encoded_next_url = base64.urlsafe_b64encode(next_url.encode('utf-8')).decode('utf-8')
        state_param = f"qq_oauth_{encoded_next_url}"
        
        auth_url = (
            f"https://graph.qq.com/oauth2.0/authorize"
            f"?response_type=code&client_id={QQ_APPID}&redirect_uri={REDIRECT_URI}"
            f"&state={state_param}&unionid=1"
        )
        logger.info(f"[OAuth Login] Redirecting to QQ auth: {auth_url}")
        return redirect(auth_url)
    
    else:
        return HttpResponse(f'不支持的登录方式: {provider}', status=400)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def oauth_login_callback_acwing(request):
    """AcWing登录回调处理"""
    from django.conf import settings
    
    code = request.GET.get('code')
    if not code:
        return HttpResponse('缺少授权码', status=400)
    
    # 获取存储的 next_url
    next_url = request.session.pop('oauth_next_url', '/oauth/authorize')
    
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    
    try:
        # 获取 access_token 和 openid
        token_url = (
            f"https://www.acwing.com/third_party/api/oauth2/access_token/"
            f"?appid={ACWING_APPID}&secret={ACWING_SECRET}&code={code}"
        )
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            logger.error(f"[OAuth Login] AcWing token error: {token_data}")
            return HttpResponse('获取token失败', status=400)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        
        # 获取用户信息
        userinfo_url = (
            f"https://www.acwing.com/third_party/api/meta/identity/getinfo/"
            f"?access_token={access_token}&openid={openid}"
        )
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if 'errcode' in userinfo_data:
            logger.error(f"[OAuth Login] AcWing userinfo error: {userinfo_data}")
            return HttpResponse('获取用户信息失败', status=400)
        
        username = userinfo_data['username']
        photo_url = userinfo_data.get('photo', '')
        
        # 查找或创建用户
        acwing_user = AcWingUser.objects.filter(openid=openid).first()
        
        if acwing_user:
            user = acwing_user.user
        else:
            # 创建新用户
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(username=username, password=None)
            AcWingUser.objects.create(
                user=user,
                openid=openid,
                access_token=access_token,
                photo_url=photo_url
            )
        
        # 使用Django的login函数设置session
        django_login(request, user)
        logger.info(f"[OAuth Login] User {user.id} logged in via AcWing, redirecting to {next_url}")
        
        # 重定向回OAuth授权页面
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"[OAuth Login] AcWing login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def oauth_login_callback_qq(request):
    """
    QQ登录回调处理（统一处理OAuth登录和普通QQ登录）
    
    这个函数被 /qq/callback 路由调用，QQ开放平台只能配置一个回调地址
    通过检查 session 中的 oauth_next_url 来判断是OAuth流程还是普通登录流程
    """
    from django.conf import settings
    from django.contrib.auth import login as django_login
    from django.contrib.auth.models import User
    from ...models import QQUser
    
    code = request.GET.get('code')
    if not code:
        return HttpResponse('缺少授权码', status=400)
    
    # 获取存储的 next_url（OAuth流程会在session中存储）
    # 如果没有，尝试从 state 参数或 referer 中恢复
    next_url = request.session.pop('oauth_next_url', None)
    is_oauth_flow = next_url is not None
    
    logger.info(f"[QQ Callback] Initial check: is_oauth_flow={is_oauth_flow}, next_url={next_url}")
    
    if not is_oauth_flow:
        logger.warning(f"[QQ Callback] No oauth_next_url in session, checking state parameter")
        # Session 可能在跨域名时丢失（QQ授权在 graph.qq.com，回调回到我们的域名）
        # 尝试从 state 参数中解析 next_url（我们在授权时将 next_url 编码到了 state 中）
        state = request.GET.get('state', '')
        logger.info(f"[QQ Callback] State parameter: {state[:100]}")  # 只记录前100个字符
        
        if state and state.startswith('qq_oauth_'):
            try:
                import base64
                encoded_next_url = state.replace('qq_oauth_', '')
                decoded_next_url = base64.urlsafe_b64decode(encoded_next_url.encode('utf-8')).decode('utf-8')
                next_url = decoded_next_url
                is_oauth_flow = True
                logger.info(f"[QQ Callback] ✅ Recovered next_url from state parameter: {next_url}")
            except Exception as e:
                logger.error(f"[QQ Callback] ❌ Failed to decode next_url from state: {str(e)}")
                # 如果解析失败，尝试从 referer 获取
                referer = request.META.get('HTTP_REFERER', '')
                logger.info(f"[QQ Callback] Checking referer: {referer}")
                if referer and 'oauth/authorize' in referer:
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(referer)
                    # 重建完整的授权URL，包括查询参数
                    query_params = parse_qs(parsed.query)
                    if query_params:
                        from urllib.parse import urlencode
                        query_string = urlencode(query_params, doseq=True)
                        next_url = f"{parsed.path}?{query_string}"
                    else:
                        next_url = parsed.path
                    is_oauth_flow = True
                    logger.info(f"[QQ Callback] ✅ Recovered next_url from referer: {next_url}")
                else:
                    # 最后尝试从 GET 参数中获取原始请求参数
                    # QQ可能不会保留原始参数，但我们可以尝试重建
                    next_url = None  # 设置为None，后续会处理
                    logger.warning(f"[QQ Callback] Could not recover next_url from state or referer")
        
        # 如果 state 不包含我们的标记，检查是否是QQ的默认state
        elif state == 'qq':
            # QQ默认state，可能是从普通QQ登录来的，不是OAuth流程
            logger.info(f"[QQ Callback] QQ default state 'qq' detected, might be normal QQ login")
            referer = request.META.get('HTTP_REFERER', '')
            if referer and 'oauth/authorize' in referer:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(referer)
                query_params = parse_qs(parsed.query)
                if query_params:
                    from urllib.parse import urlencode
                    query_string = urlencode(query_params, doseq=True)
                    next_url = f"{parsed.path}?{query_string}"
                else:
                    next_url = parsed.path
                is_oauth_flow = True
                logger.info(f"[QQ Callback] ✅ Recovered next_url from referer (state=qq): {next_url}")
        
        # 如果还是没有找到 next_url，尝试从 referer 获取（即使没有state标记）
        if not is_oauth_flow or not next_url:
            referer = request.META.get('HTTP_REFERER', '')
            logger.info(f"[QQ Callback] Final check - referer: {referer}, current is_oauth_flow: {is_oauth_flow}, next_url: {next_url}")
            if referer and 'oauth/authorize' in referer:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(referer)
                query_params = parse_qs(parsed.query)
                if query_params:
                    from urllib.parse import urlencode
                    query_string = urlencode(query_params, doseq=True)
                    next_url = f"{parsed.path}?{query_string}"
                else:
                    next_url = parsed.path
                is_oauth_flow = True
                logger.info(f"[QQ Callback] ✅ Recovered next_url from referer (fallback): {next_url}")
        
        # 如果还是没有 next_url，说明可能不是OAuth流程，或者参数丢失了
        # 再次尝试从 referer 恢复（即使之前检查过，但可能在前面的逻辑中 next_url 被设置为None）
        if not next_url or not is_oauth_flow:
            # 尝试从请求头中获取原始授权页面的URL（如果浏览器保留了）
            referer = request.META.get('HTTP_REFERER', '')
            logger.info(f"[QQ Callback] Last attempt - referer: {referer}")
            if referer and 'oauth/authorize' in referer:
                # 即使之前失败了，再次尝试从referer恢复
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(referer)
                query_params = parse_qs(parsed.query)
                if query_params:
                    from urllib.parse import urlencode
                    query_string = urlencode(query_params, doseq=True)
                    next_url = f"{parsed.path}?{query_string}"
                else:
                    next_url = parsed.path
                is_oauth_flow = True
                logger.info(f"[QQ Callback] ✅ Recovered next_url from referer (last attempt): {next_url}")
            elif not next_url:
                # 如果确实无法恢复 next_url，设置为默认值，但标记为OAuth流程
                # 这样至少会重定向到授权页面，虽然可能缺少参数
                logger.warning(f"[QQ Callback] ❌ Could not recover next_url, will redirect to default authorization page")
                # 尝试从请求的原始URL中获取参数（如果有的话）
                # 但这通常不可靠，因为回调请求是GET请求，参数已经被QQ处理了
                next_url = '/oauth/authorize'  # 默认值，虽然缺少参数，但至少会显示错误信息
                is_oauth_flow = True  # 假设这是OAuth流程，因为从授权页面来的
    
    QQ_APPID = getattr(settings, 'QQ_APPID', '')
    QQ_APPKEY = getattr(settings, 'QQ_APPKEY', '')
    
    try:
        # 获取 access_token
        # 注意：回调地址必须与授权时的地址完全一致
        # 统一使用 /qq/callback，与QQ开放平台配置的回调地址保持一致
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/qq/callback"
        token_url = (
            f"https://graph.qq.com/oauth2.0/token"
            f"?grant_type=authorization_code&client_id={QQ_APPID}"
            f"&client_secret={QQ_APPKEY}&code={code}"
            f"&redirect_uri={REDIRECT_URI}"
        )
        token_response = requests.get(token_url, timeout=10)
        token_text = token_response.text
        
        # 解析 token 响应（可能是 URL 编码格式）
        if 'error' in token_text:
            logger.error(f"[OAuth Login] QQ token error: {token_text}")
            return HttpResponse('获取token失败', status=400)
        
        # 解析 access_token
        import re
        access_token_match = re.search(r'access_token=([^&]+)', token_text)
        if not access_token_match:
            return HttpResponse('获取token失败', status=400)
        
        access_token = access_token_match.group(1)
        
        # 获取 openid 和 unionid
        openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"
        openid_response = requests.get(openid_url, timeout=10)
        openid_text = openid_response.text
        
        # 解析 JSONP 响应
        import json
        openid_data = json.loads(openid_text.strip().lstrip('callback(').rstrip(');'))
        openid = openid_data.get('openid')
        unionid = openid_data.get('unionid', '')
        
        # 获取用户信息
        userinfo_url = (
            f"https://graph.qq.com/user/get_user_info"
            f"?access_token={access_token}&oauth_consumer_key={QQ_APPID}&openid={openid}"
        )
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if userinfo_data.get('ret') != 0:
            logger.error(f"[OAuth Login] QQ userinfo error: {userinfo_data}")
            return HttpResponse('获取用户信息失败', status=400)
        
        nickname = userinfo_data.get('nickname', 'QQ用户')
        avatar = userinfo_data.get('figureurl_qq_2', '')
        
        # 查找或创建用户
        qq_user = QQUser.objects.filter(openid=openid).first()
        
        if qq_user:
            user = qq_user.user
        else:
            # 创建新用户
            base_username = nickname
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(username=username, password=None)
            QQUser.objects.create(
                user=user,
                openid=openid,
                unionid=unionid,
                nickname=nickname,
                avatar=avatar
            )
        
        # 使用Django的login函数设置session
        django_login(request, user)
        logger.info(f"[QQ Callback] User {user.id} logged in via QQ, is_oauth_flow: {is_oauth_flow}, next_url: {next_url}")
        
        # 如果是OAuth流程，重定向回授权页面（带原始参数）
        if is_oauth_flow and next_url:
            # 确保 next_url 包含完整的OAuth授权URL和参数
            # next_url 应该已经是完整的URL，如 /oauth/authorize?client_id=xxx&...
            # 如果 next_url 是相对路径，确保它以 / 开头
            if not next_url.startswith('/'):
                next_url = '/' + next_url
            
            # 如果 next_url 不包含查询参数，尝试从其他来源恢复参数
            # 但这通常不太可能，因为我们之前已经尝试从 referer 恢复了
            if '?' not in next_url:
                logger.warning(f"[QQ Callback] next_url does not contain query parameters: {next_url}")
                # 即使没有参数，也重定向，让授权页面显示错误信息（这比停留在主界面好）
            
            logger.info(f"[QQ Callback] ✅ Redirecting to authorization page: {next_url}")
            return redirect(next_url)
        else:
            # 如果不是OAuth流程，或者无法恢复 next_url
            # 显示一个提示页面，让用户手动返回授权页面
            logger.warning(f"[QQ Callback] ⚠️ OAuth flow not detected or next_url missing. is_oauth_flow: {is_oauth_flow}, next_url: {next_url}")
            
            # 尝试从 referer 获取原始授权页面（最后一次尝试）
            referer = request.META.get('HTTP_REFERER', '')
            redirect_url = '/oauth/authorize'  # 默认值
            
            if referer and 'oauth/authorize' in referer:
                # 从 referer 提取完整的授权URL
                from urllib.parse import urlparse
                parsed = urlparse(referer)
                redirect_url = f"{parsed.path}?{parsed.query}" if parsed.query else parsed.path
                logger.info(f"[QQ Callback] Using referer as redirect URL: {redirect_url}")
            
            # 显示提示页面，自动重定向
            return HttpResponse(
                f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>QQ登录成功 - 正在返回授权页面</title>
                    <meta http-equiv="refresh" content="2;url={redirect_url}">
                </head>
                <body style="font-family: Arial, sans-serif; padding: 30px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;">
                    <div style="background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2); max-width: 500px;">
                        <h1 style="color: #28a745; font-size: 28px; margin-bottom: 20px;">✅ QQ登录成功！</h1>
                        <p style="font-size: 16px; color: #606266; margin-bottom: 20px;">您已成功登录，正在返回授权页面...</p>
                        <p style="font-size: 14px; color: #909399;">
                            如果没有自动跳转，请
                            <a href="{redirect_url}" style="color: #667eea; text-decoration: none;">点击这里</a>
                            返回授权页面。
                        </p>
                    </div>
                    <script>
                        // 备用：如果 meta refresh 不工作，使用 JavaScript 重定向
                        setTimeout(() => {{
                            window.location.href = '{redirect_url}';
                        }}, 2000);
                    </script>
                </body>
                </html>
                ''',
                content_type='text/html; charset=utf-8'
            )
        
    except Exception as e:
        logger.error(f"[OAuth Login] QQ login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)

