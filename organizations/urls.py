from django.urls import path, include
from rest_framework_nested import routers

from events.views import EventViewSet
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

eventRouter = routers.NestedDefaultRouter(
    router, r"organizations", lookup="organization"
)
eventRouter.register(r"events", EventViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(organizationRouter.urls)),
    path("", include(eventRouter.urls)),
]
