# Generated manually for AcWingUser model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0004_merge_20251107_0811'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcWingUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=100, unique=True, verbose_name='AcWing OpenID')),
                ('access_token', models.CharField(blank=True, max_length=200, verbose_name='访问令牌')),
                ('refresh_token', models.CharField(blank=True, max_length=200, verbose_name='刷新令牌')),
                ('photo_url', models.URLField(blank=True, verbose_name='头像URL')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='acwing_profile', to=settings.AUTH_USER_MODEL, verbose_name='关联用户')),
            ],
            options={
                'verbose_name': 'AcWing用户',
                'verbose_name_plural': 'AcWing用户列表',
            },
        ),
    ]

