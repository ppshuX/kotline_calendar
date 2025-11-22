"""
URL configuration for calendar_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Import QQ callback handler
from api.views.oauth.login import oauth_login_callback_qq

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # QQ回调地址（必须在根路径，因为QQ开放平台只能配置一个回调地址）
    # 统一使用 /qq/callback，同时处理OAuth登录和普通QQ登录
    path('qq/callback', oauth_login_callback_qq, name='qq_callback'),
    
    # 法律文档页面
    path('terms', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    
    # OAuth 2.0 路由（需要在根路径，因为第三方应用可能直接访问 /oauth/authorize）
    path('oauth/', include('api.url_patterns.oauth')),
    
    # API 路由
    path('api/', include('api.urls')),        # 保留旧版本（向后兼容）
    path('api/v1/', include('api.urls')),     # v1 版本（Roamio 对接使用）
    path('api-auth/', include('rest_framework.urls')),
]

# 提供静态文件（在生产环境也需要）
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
