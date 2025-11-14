"""
OAuth 2.0 相关视图
"""
from .authorize import oauth_authorize
from .token import oauth_token
from .userinfo import oauth_userinfo
from .revoke import oauth_revoke

__all__ = [
    'oauth_authorize',
    'oauth_token',
    'oauth_userinfo',
    'oauth_revoke',
]

