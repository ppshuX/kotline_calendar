# Generated migration for OAuth 2.0 models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0008_add_qq_unionid'),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(db_index=True, max_length=100, unique=True, help_text='客户端唯一标识符')),
                ('client_secret_hash', models.CharField(max_length=255, help_text='客户端密钥（加密存储）')),
                ('client_name', models.CharField(max_length=100, help_text='应用名称，例如：Roamio')),
                ('client_description', models.TextField(blank=True, help_text='应用描述')),
                ('redirect_uris', models.JSONField(default=list, help_text='允许的回调地址列表')),
                ('allowed_scopes', models.JSONField(default=list, help_text='允许的权限范围列表')),
                ('is_active', models.BooleanField(default=True, help_text='是否激活')),
                ('logo_url', models.URLField(blank=True, help_text='应用Logo URL')),
                ('website_url', models.URLField(blank=True, help_text='应用官网')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'OAuth客户端',
                'verbose_name_plural': 'OAuth客户端',
                'db_table': 'oauth_clients',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuthorizationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=100, unique=True, help_text='授权码')),
                ('redirect_uri', models.URLField(help_text='回调地址')),
                ('scope', models.CharField(max_length=200, help_text='权限范围')),
                ('expires_at', models.DateTimeField(db_index=True, help_text='过期时间')),
                ('used', models.BooleanField(db_index=True, default=False, help_text='是否已使用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorization_codes', to='api.oauthclient', help_text='关联的OAuth客户端')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorization_codes', to=settings.AUTH_USER_MODEL, help_text='关联的用户')),
            ],
            options={
                'verbose_name': '授权码',
                'verbose_name_plural': '授权码',
                'db_table': 'oauth_authorization_codes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OAuthAccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=500, unique=True, help_text='访问令牌（JWT格式）')),
                ('refresh_token', models.CharField(db_index=True, max_length=500, blank=True, null=True, help_text='刷新令牌')),
                ('scope', models.CharField(max_length=200, help_text='权限范围')),
                ('expires_at', models.DateTimeField(db_index=True, help_text='过期时间')),
                ('is_revoked', models.BooleanField(db_index=True, default=False, help_text='是否已撤销')),
                ('last_used_at', models.DateTimeField(null=True, blank=True, help_text='最后使用时间')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_tokens', to='api.oauthclient', help_text='关联的OAuth客户端')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth_access_tokens', to=settings.AUTH_USER_MODEL, help_text='关联的用户')),
            ],
            options={
                'verbose_name': 'OAuth访问令牌',
                'verbose_name_plural': 'OAuth访问令牌',
                'db_table': 'oauth_access_tokens',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='oauthaccesstoken',
            index=models.Index(fields=['user', 'client', 'is_revoked'], name='oauth_token_user_client_idx'),
        ),
        migrations.AddIndex(
            model_name='oauthaccesstoken',
            index=models.Index(fields=['expires_at', 'is_revoked'], name='oauth_token_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='oauthaccesstoken',
            index=models.Index(fields=['refresh_token'], name='oauth_token_refresh_idx'),
        ),
    ]

