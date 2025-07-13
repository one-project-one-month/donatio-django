from .views import EventListViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r"events", EventListViewSet, basename="events")

urlpatterns = router.urls
