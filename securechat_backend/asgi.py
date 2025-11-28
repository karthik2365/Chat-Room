import os
from django.core.asgi import get_asgi_application

# 1) Ensure DJANGO_SETTINGS_MODULE is set before importing Django internals
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "securechat_backend.settings")

# 2) Setup Django
import django
django.setup()

# 3) Channels imports
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# 4) Import your chat routing AFTER Django setup
import chat.routing

# 5) Build application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})