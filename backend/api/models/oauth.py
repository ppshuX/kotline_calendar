"""
OAuth 2.0 数据模型
实现标准的 OAuth 2.0 Authorization Code Flow
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
import secrets
import logging

logger = logging.getLogger(__name__)


class OAuthClient(models.Model):
    """
    OAuth 客户端（第三方应用）
    
    代表接入 Ralendar 的第三方应用（如 Roamio）
    """
    client_id = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True,
        help_text="客户端唯一标识符"
    )
    client_secret_hash = models.CharField(
        max_length=255,
        help_text="客户端密钥（加密存储）"
    )
    client_name = models.CharField(
        max_length=100,
        help_text="应用名称，例如：Roamio"
    )
    client_description = models.TextField(
        blank=True,
        help_text="应用描述"
    )
    redirect_uris = models.JSONField(
        default=list,
        help_text="允许的回调地址列表"
    )
    allowed_scopes = models.JSONField(
        default=list,
        help_text="允许的权限范围列表"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="是否激活"
    )
    logo_url = models.URLField(
        blank=True,
        help_text="应用Logo URL"
    )
    website_url = models.URLField(
        blank=True,
        help_text="应用官网"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'oauth_clients'
        verbose_name = 'OAuth客户端'
        verbose_name_plural = 'OAuth客户端'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client_name} ({self.client_id})"
    
    def set_secret(self, raw_secret):
        """设置客户端密钥（加密存储）"""
        self.client_secret_hash = make_password(raw_secret)
    
    def verify_secret(self, raw_secret):
        """验证客户端密钥"""
        return check_password(raw_secret, self.client_secret_hash)
    
    def is_redirect_uri_allowed(self, uri):
        """验证回调地址是否在白名单内"""
        return uri in self.redirect_uris
    
    def is_scope_allowed(self, scope_string):
        """验证权限范围是否允许"""
        requested_scopes = set(scope_string.split())
        allowed_scopes = set(self.allowed_scopes)
        return requested_scopes.issubset(allowed_scopes)
    
    @classmethod
    def generate_client_credentials(cls):
        """生成客户端ID和密钥"""
        client_id = f"ralendar_client_{secrets.token_urlsafe(16)}"
        client_secret = secrets.token_urlsafe(32)
        return client_id, client_secret


class AuthorizationCode(models.Model):
    """
    授权码
    
    临时存储，用于换取 access_token
    特性：
    - 10分钟有效期
    - 一次性使用
    - 绑定到特定的 client 和 user
    """
    code = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True,
        help_text="授权码"
    )
    client = models.ForeignKey(
        OAuthClient, 
        on_delete=models.CASCADE,
        related_name='authorization_codes',
        help_text="关联的OAuth客户端"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='authorization_codes',
        help_text="授权的用户"
    )
    redirect_uri = models.CharField(
        max_length=500,
        help_text="回调地址"
    )
    scope = models.CharField(
        max_length=200,
        help_text="授权的权限范围"
    )
    state = models.CharField(
        max_length=200,
        blank=True,
        help_text="防CSRF的状态参数"
    )
    expires_at = models.DateTimeField(
        help_text="过期时间"
    )
    used = models.BooleanField(
        default=False,
        db_index=True,
        help_text="是否已使用"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'oauth_authorization_codes'
        verbose_name = '授权码'
        verbose_name_plural = '授权码'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.code[:10]}... for {self.user.username}"
    
    @classmethod
    def create_code(cls, client, user, redirect_uri, scope, state=''):
        """创建授权码"""
        code = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(minutes=10)
        
        auth_code = cls.objects.create(
            code=code,
            client=client,
            user=user,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            expires_at=expires_at
        )
        
        logger.info(f"[OAuth] Authorization code created for user {user.id}, client {client.client_name}")
        return auth_code
    
    def is_valid(self):
        """检查授权码是否有效"""
        if self.used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """标记为已使用"""
        self.used = True
        self.save(update_fields=['used'])
        logger.info(f"[OAuth] Authorization code {self.code[:10]}... marked as used")
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的授权码"""
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        if expired_count > 0:
            logger.info(f"[OAuth] Cleaned up {expired_count} expired authorization codes")
        return expired_count


class OAuthAccessToken(models.Model):
    """
    访问令牌
    
    用于访问受保护的 API
    特性：
    - 2小时有效期（可配置）
    - 可撤销
    - 绑定到特定的 client 和 user
    - 包含权限范围
    """
    token = models.CharField(
        max_length=500, 
        unique=True, 
        db_index=True,
        help_text="访问令牌（JWT格式）"
    )
    client = models.ForeignKey(
        OAuthClient, 
        on_delete=models.CASCADE,
        related_name='access_tokens',
        help_text="关联的OAuth客户端"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='oauth_access_tokens',
        help_text="关联的用户"
    )
    scope = models.CharField(
        max_length=200,
        help_text="权限范围"
    )
    expires_at = models.DateTimeField(
        help_text="过期时间"
    )
    refresh_token = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        db_index=True,
        help_text="刷新令牌"
    )
    is_revoked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="是否已撤销"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="最后使用时间"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'oauth_access_tokens'
        verbose_name = '访问令牌'
        verbose_name_plural = '访问令牌'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'client', 'is_revoked']),
            models.Index(fields=['expires_at', 'is_revoked']),
            models.Index(fields=['refresh_token']),
        ]
    
    def __str__(self):
        return f"Token for {self.user.username} - {self.client.client_name}"
    
    @classmethod
    def create_token(cls, client, user, scope, token_string, refresh_token_string=None, expires_in=7200):
        """创建访问令牌"""
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        
        access_token = cls.objects.create(
            token=token_string,
            client=client,
            user=user,
            scope=scope,
            expires_at=expires_at,
            refresh_token=refresh_token_string
        )
        
        logger.info(f"[OAuth] Access token created for user {user.id}, client {client.client_name}, scope: {scope}")
        return access_token
    
    def is_valid(self):
        """检查令牌是否有效"""
        if self.is_revoked:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def has_scope(self, required_scope):
        """检查是否包含所需的权限"""
        token_scopes = set(self.scope.split())
        required_scopes = set(required_scope.split())
        return required_scopes.issubset(token_scopes)
    
    def revoke(self):
        """撤销令牌"""
        self.is_revoked = True
        self.save(update_fields=['is_revoked'])
        logger.info(f"[OAuth] Access token revoked for user {self.user.id}, client {self.client.client_name}")
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的令牌"""
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now() - timedelta(days=7)  # 保留7天的过期记录
        ).delete()[0]
        if expired_count > 0:
            logger.info(f"[OAuth] Cleaned up {expired_count} expired access tokens")
        return expired_count
    
    @classmethod
    def revoke_all_for_client(cls, user, client):
        """撤销用户对某个客户端的所有令牌"""
        count = cls.objects.filter(
            user=user,
            client=client,
            is_revoked=False
        ).update(is_revoked=True)
        logger.info(f"[OAuth] Revoked {count} tokens for user {user.id}, client {client.client_name}")
        return count


# OAuth 权限范围定义
OAUTH_SCOPES = {
    'calendar:read': '查看日历事件',
    'calendar:write': '创建和编辑日历事件',
    'calendar:delete': '删除日历事件',
    'user:read': '读取用户基本信息',
}


def get_scope_description(scope_string):
    """获取权限范围的描述"""
    scopes = scope_string.split()
    descriptions = []
    for scope in scopes:
        description = OAUTH_SCOPES.get(scope, scope)
        descriptions.append(description)
    return descriptions

