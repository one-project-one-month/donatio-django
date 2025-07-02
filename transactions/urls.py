from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")

urlpatterns = router.urls
