"""
ASGI config for chatapi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat_channels.middleware import JWTAuthMiddleware, CatchRoutingErrorsMiddleware

import chat_channels.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapi.settings')

# application = get_asgi_application()


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": CatchRoutingErrorsMiddleware(
        JWTAuthMiddleware(
        URLRouter(
            chat_channels.routing.websocket_urlpatterns
        )
    ),),
})

