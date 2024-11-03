from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception:
        return None

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self.inner)


class JWTAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = scope
        self.inner = inner
        self.instance = None

    async def __call__(self, receive, send):
        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            self.scope["user"] = await get_user_from_token(token[0])
        else:
            self.scope["user"] = None

        inner = self.inner(self.scope)
        return await inner(receive, send)
