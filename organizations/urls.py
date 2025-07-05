from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    OrganizationRequestViewSet,
    OrganizationViewSet,
    OrganizationChatViewSet,
)

router = routers.DefaultRouter()
router.register(
    r"organization-requests",
    OrganizationRequestViewSet,
    basename="organization-requests",
)
router.register(r"organizations", OrganizationViewSet, basename="organizations")

organizationRouter = routers.NestedDefaultRouter(
    router, r"organizations", lookup="organization"
)
organizationRouter.register(
    r"chats", OrganizationChatViewSet, basename="organization-chats"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(organizationRouter.urls)),
]
