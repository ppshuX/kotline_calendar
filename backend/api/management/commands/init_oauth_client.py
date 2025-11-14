"""
初始化 OAuth 客户端
为 Roamio 创建 OAuth 客户端配置
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from api.models import OAuthClient


class Command(BaseCommand):
    help = '初始化 OAuth 客户端（为 Roamio 创建配置）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-name',
            type=str,
            default='Roamio',
            help='客户端名称'
        )
        parser.add_argument(
            '--client-id',
            type=str,
            help='客户端ID（不提供则自动生成）'
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='客户端密钥（不提供则自动生成）'
        )
        parser.add_argument(
            '--redirect-uris',
            type=str,
            help='回调地址（逗号分隔），例如：https://roamio.cn/auth/callback,http://localhost:8080/auth/callback'
        )

    def handle(self, *args, **options):
        client_name = options['client_name']
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        redirect_uris_str = options.get('redirect_uris')

        # 生成客户端凭证
        if not client_id or not client_secret:
            client_id, client_secret = OAuthClient.generate_client_credentials()
            self.stdout.write(self.style.SUCCESS('\n=== 自动生成的客户端凭证 ==='))
        else:
            self.stdout.write(self.style.SUCCESS('\n=== 使用提供的客户端凭证 ==='))

        # 解析回调地址
        redirect_uris = []
        if redirect_uris_str:
            redirect_uris = [uri.strip() for uri in redirect_uris_str.split(',')]
        else:
            # 默认回调地址
            redirect_uris = [
                'https://roamio.cn/auth/ralendar/callback',
                'http://localhost:8080/auth/ralendar/callback',  # 开发环境
            ]

        # 检查客户端是否已存在
        existing_client = OAuthClient.objects.filter(client_id=client_id).first()
        if existing_client:
            self.stdout.write(self.style.WARNING(f'\n客户端 "{client_id}" 已存在！'))
            
            # 询问是否更新
            confirm = input('是否更新现有配置？(yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('操作已取消'))
                return

            # 更新客户端
            existing_client.client_name = client_name
            existing_client.set_secret(client_secret)
            existing_client.redirect_uris = redirect_uris
            existing_client.allowed_scopes = [
                'calendar:read',
                'calendar:write',
                'user:read'
            ]
            existing_client.save()

            self.stdout.write(self.style.SUCCESS(f'\n✅ OAuth 客户端已更新：{client_name}'))
        else:
            # 创建新客户端
            client = OAuthClient(
                client_id=client_id,
                client_name=client_name,
                client_description=f'{client_name} 旅行规划应用',
                redirect_uris=redirect_uris,
                allowed_scopes=[
                    'calendar:read',
                    'calendar:write',
                    'user:read'
                ],
                is_active=True
            )
            client.set_secret(client_secret)
            client.save()

            self.stdout.write(self.style.SUCCESS(f'\n✅ OAuth 客户端已创建：{client_name}'))

        # 显示配置信息
        self.stdout.write(self.style.SUCCESS('\n=== 客户端配置信息 ==='))
        self.stdout.write(f'Client ID:     {client_id}')
        self.stdout.write(f'Client Secret: {client_secret}')
        self.stdout.write(f'Client Name:   {client_name}')
        self.stdout.write(f'Redirect URIs:')
        for uri in redirect_uris:
            self.stdout.write(f'  - {uri}')
        self.stdout.write(f'Allowed Scopes:')
        self.stdout.write(f'  - calendar:read')
        self.stdout.write(f'  - calendar:write')
        self.stdout.write(f'  - user:read')

        self.stdout.write(self.style.SUCCESS('\n=== 请将以下信息提供给 Roamio 团队 ==='))
        self.stdout.write(f'CLIENT_ID={client_id}')
        self.stdout.write(f'CLIENT_SECRET={client_secret}')
        self.stdout.write(f'\n⚠️  请妥善保管 Client Secret，不要泄露！')

