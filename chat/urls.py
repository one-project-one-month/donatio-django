from rest_framework_nested import routers
from .views import ChatMessageViewSet, ChatViewSet

router = routers.DefaultRouter()
router.register(r"chats", ChatViewSet, basename="chats")
router.register(r"messages", ChatMessageViewSet, basename="messages")

urlpatterns = router.urls
