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
        headers = dict(scope["headers"])
        # All keys and values are bytes, not strings in this header dict
        cookie_header = headers.get(b"cookie", "").decode("utf-8")
        token = None
        # Get "access_token" from cookie header
        for part in cookie_header.split(";"):
            if part.strip().startswith("access_token="):
                # Split the part by "=" and strip both ends
                # Then the second part or the last part which is the token
                token = part.strip().split("=")[1]
                break
        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)
