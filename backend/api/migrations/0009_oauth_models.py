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
                ('client_id', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='客户端ID')),
                ('client_secret_hash', models.CharField(max_length=255, verbose_name='客户端密钥哈希')),
                ('client_name', models.CharField(max_length=100, verbose_name='客户端名称')),
                ('redirect_uris', models.JSONField(default=list, verbose_name='回调地址列表')),
                ('allowed_scopes', models.JSONField(default=list, verbose_name='允许的权限范围')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': 'OAuth客户端',
                'verbose_name_plural': 'OAuth客户端',
                'db_table': 'oauth_client',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuthorizationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='授权码')),
                ('redirect_uri', models.URLField(verbose_name='回调地址')),
                ('scope', models.CharField(max_length=255, verbose_name='权限范围')),
                ('expires_at', models.DateTimeField(db_index=True, verbose_name='过期时间')),
                ('used', models.BooleanField(db_index=True, default=False, verbose_name='是否已使用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorization_codes', to='api.oauthclient', verbose_name='客户端')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorization_codes', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '授权码',
                'verbose_name_plural': '授权码',
                'db_table': 'oauth_authorization_code',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OAuthAccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=500, unique=True, verbose_name='访问令牌')),
                ('refresh_token', models.CharField(db_index=True, max_length=500, verbose_name='刷新令牌')),
                ('scope', models.CharField(max_length=255, verbose_name='权限范围')),
                ('expires_at', models.DateTimeField(db_index=True, verbose_name='过期时间')),
                ('is_revoked', models.BooleanField(db_index=True, default=False, verbose_name='是否已撤销')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_tokens', to='api.oauthclient', verbose_name='客户端')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth_tokens', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': 'OAuth访问令牌',
                'verbose_name_plural': 'OAuth访问令牌',
                'db_table': 'oauth_access_token',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='oauthaccesstoken',
            index=models.Index(fields=['token', 'is_revoked'], name='oauth_acces_token_7b8e5f_idx'),
        ),
        migrations.AddIndex(
            model_name='oauthaccesstoken',
            index=models.Index(fields=['refresh_token', 'is_revoked'], name='oauth_acces_refresh_8a3d2c_idx'),
        ),
        migrations.AddIndex(
            model_name='authorizationcode',
            index=models.Index(fields=['code', 'used'], name='oauth_autho_code_4f9a1b_idx'),
        ),
    ]

