from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import GoogleLoginSerializer, ProfileSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Profile
from attachments.models import Attachment
from .serializers import CustomUserDetailsSerializer
from django.shortcuts import get_object_or_404


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = GoogleLoginSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserDetailsSerializer
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_staff"]

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=["get", "put"], url_path="me")
    def current_user(self, request):
        # Return the current authenticated user
        if request.method == "GET":
            user = self.request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Update the current authenticated user profile
        elif request.method == "PUT":
            profile = get_object_or_404(Profile, user=request.user)

            serializer = ProfileSerializer(profile, data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if request.FILES.get("profile_picture"):
                try:
                    # Delete all existing attachments
                    profile.attachments.all().delete()

                    # Create new attachment
                    profile_picture = request.FILES.get("profile_picture")
                    if not profile_picture:
                        return Response(
                            {"error": "No profile picture file provided"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    attachment = Attachment.objects.create(
                        content_object=profile, file=profile_picture
                    )
                except ValueError as e:
                    return Response(
                        {"error": f"Invalid file format: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except Exception as e:
                    return Response(
                        {
                            "error": f"Failed to create profile picture attachment: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            try:
                serializer.save()
            except Exception:
                return Response(
                    {"error": "Failed to save profile"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(serializer.data, status=status.HTTP_200_OK)
