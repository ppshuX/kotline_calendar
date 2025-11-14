"""
OAuth 2.0 相关路由
"""
from django.urls import path
from ..views import (
    oauth_authorize,
    oauth_token,
    oauth_userinfo,
    oauth_revoke,
    oauth_authorized_apps,
)

urlpatterns = [
    # 授权端点（用户授权页面）
    path('authorize', oauth_authorize, name='oauth_authorize'),
    
    # Token 端点（获取/刷新访问令牌）
    path('token', oauth_token, name='oauth_token'),
    
    # UserInfo 端点（获取用户信息）
    path('userinfo', oauth_userinfo, name='oauth_userinfo'),
    
    # Token 撤销端点
    path('revoke', oauth_revoke, name='oauth_revoke'),
    
    # 已授权应用列表
    path('authorized-apps', oauth_authorized_apps, name='oauth_authorized_apps'),
]

