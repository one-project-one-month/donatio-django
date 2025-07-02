from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OrganizationRequest, Organization
from .constants import OrganizationRequestStatus

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrganizationRequestSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer(read_only=True)
    submitted_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='submitted_by', write_only=True, required=False
    )

    approved_by = UserSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='approved_by', write_only=True, required=False
    )

    status = serializers.ChoiceField(choices=OrganizationRequestStatus.choices, required=False)

    class Meta:
        model = OrganizationRequest
        fields = [
            'id', 'submitted_by', 'submitted_by_id', 'organization_name', 'status',
            'approved_by', 'approved_by_id', 'approved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['approved_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        if 'submitted_by' not in validated_data and self.context['request'].user.is_authenticated:
            validated_data['submitted_by'] = self.context['request'].user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            new_status = validated_data['status']
            if new_status == OrganizationRequestStatus.APPROVED and instance.status != OrganizationRequestStatus.APPROVED:
                instance.approved_by = self.context['request'].user
                instance.approved_at = serializers.DateTimeField().to_internal_value(serializers.DateTimeField().now())
            elif new_status != OrganizationRequestStatus.APPROVED and instance.status == OrganizationRequestStatus.APPROVED:
                instance.approved_by = None
                instance.approved_at = None
        
        return super().update(instance, validated_data)


class OrganizationSerializer(serializers.ModelSerializer):

    admin = UserSerializer(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='admin', write_only=True, required=False
    )

    organization_request = OrganizationRequestSerializer(read_only=True)
    organization_request_id = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationRequest.objects.all(), source='organization_request', write_only=True
    )

    class Meta:
        model = Organization
        fields = [
            'id', 'admin', 'admin_id', 'name', 'description', 'phone_number', 'email',
            'additional_info', 'organization_request', 'organization_request_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at','updated_at']

    def create(self, validated_data):
        if 'admin' not in validated_data and self.context['request'].user.is_staff:
            validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)