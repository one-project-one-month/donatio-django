from rest_framework_nested import routers
from .views import ActivityListViewSet

router = routers.DefaultRouter()
router.register(r"activities", ActivityListViewSet, basename="activities")

urlpatterns = router.urls