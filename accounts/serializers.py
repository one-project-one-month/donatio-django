from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from .models import Profile, User
from organizations.models import Organization


class GoogleLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        # Use id_token as access_token if needed
        if not attrs.get("access_token") and "id_token" in self.context["request"].data:
            attrs["access_token"] = self.context["request"].data["id_token"]
        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "full_name", "phone_number", "profile_picture"]

    def get_profile_picture(self, obj):
        attachment = obj.attachments.first()
        if attachment and attachment.file:
            return attachment.file.url
        return None
    
class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "full_name"]


class CustomUserDetailsSerializer(UserDetailsSerializer):
    profile = ProfileSerializer(read_only=True)
    is_org_admin = serializers.SerializerMethodField(read_only=True)
    
    class Meta(UserDetailsSerializer.Meta):
        fields = ["id", "username", "email", "is_staff", "is_superuser", "profile", "joined_at", "is_org_admin"]
        read_only_fields = ["is_staff", "is_superuser", "is_org_admin"]
    
    # True if user is an admin of one or many organizations
    def get_is_org_admin(self, obj):
        return Organization.objects.filter(admin=obj).exists()
    
#Simple User Serializer
class SimpleUserSerializer(serializers.ModelSerializer):
    profile = SimpleProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]
