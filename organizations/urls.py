from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationRequestViewSet, OrganizationViewSet

router = DefaultRouter()
router.register(
    r"organization-requests",
    OrganizationRequestViewSet,
    basename="organization-requests",
)
router.register(r"organizations", OrganizationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
