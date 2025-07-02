from rest_framework_nested import routers
from .views import UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = router.urls
