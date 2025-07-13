from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, TransactionHistoryView

router = DefaultRouter()
router.register(r"", TransactionViewSet, basename="transactions")

urlpatterns = router.urls
