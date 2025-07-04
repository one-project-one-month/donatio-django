from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')

urlpatterns = router.urls