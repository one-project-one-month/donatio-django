from django.contrib.auth.models import AnonymousUser

# get_user_model() function is Django's recommended way to get the active user model.
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        User = get_user_model()
        return User.objects.get(id=user_id)
    except Exception as err:
        print(f"Error occured: {err}")
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        # Store the ASGI application which was passed
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        token = None
        #Extract the token from the query string
        for param in query_string.split("&"):
            if param.startswith("access_token="):
                token = param.split("=")[1]
                break
            
        scope["user"] = AnonymousUser() if token is None else await get_user_from_token(token)
        
        return await self.app(scope, receive, send)
