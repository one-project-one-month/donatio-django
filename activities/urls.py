from rest_framework import routers
from .views import ActivityListView


router = routers.DefaultRouter()
router.register(r"activities", ActivityListView, basename="activity")

urlpatterns = router.urls
