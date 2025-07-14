from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from organizations.serializers import  SimpleOrganizationSerializer
from attachments.serializers import SimpleAttachmentSerializer
from transactions.serializers import TransactionSerializer
from .models import Activity, ActivityTransaction
from organizations.models import Organization
from transactions.models import Transaction
from attachments.models import Attachment

class ActivityTransactionSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)

    class Meta:
        model = ActivityTransaction
        fields = ['id', 'transaction', 'linked_at']
        read_only_fields = fields


class ActivityDetailSerializer(serializers.ModelSerializer):
    organization = SimpleOrganizationSerializer(read_only=True)
    activity_transactions = ActivityTransactionSerializer(source='transaction_links', many=True, read_only=True)
    attachments = SimpleAttachmentSerializer(many=True, read_only=True)
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta:
        model = Activity
        fields = [
            'id',
            'organization',
            'title',
            'description',
            'location',
            'created_at',
            'updated_at',
            'activity_transactions',
            'attachments',
            'transaction_ids'
        ]
        read_only_fields = ['created_at', 'updated_at', 'activity_transactions', 'attachments', 'organization']
        
    def validate_transaction_ids(self, value):
        # Check for duplicate transaction IDs
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate transaction IDs are not allowed.")
            
        return value
        
    def create(self, validated_data):
        transaction_ids = validated_data.pop('transaction_ids', [])
        attachments = validated_data.pop("uploaded_attachments", [])
        organization = get_object_or_404(Organization, id=self.context['view'].kwargs['organization_pk'])
        
        with transaction.atomic():
            # Create the activity
            activity = Activity.objects.create(**validated_data)
            
            # Process transactions
            if transaction_ids:
                # Get all valid transactions
                transactions = Transaction.objects.filter(
                    id__in=transaction_ids,
                    organization=organization,
                    type='disbursement'
                )
                
                # Check for invalid transactions
                valid_ids = set(transactions.values_list('id', flat=True))
                invalid_ids = set(transaction_ids) - valid_ids
                
                if invalid_ids:
                    raise serializers.ValidationError({
                        'transaction_ids': f"Invalid or non-disbursement transactions: {', '.join(map(str, invalid_ids))}"
                    })
                
                # Check for already linked transactions
                linked_transactions = ActivityTransaction.objects.filter(
                    transaction__id__in=valid_ids
                ).values_list('transaction__id', flat=True)
                
                if linked_transactions:
                    raise serializers.ValidationError({
                        'transaction_ids': f"Transactions already linked to other activities: {', '.join(map(str, linked_transactions))}"
                    })
                
                # Create activity transactions
                activity_transactions = [
                    ActivityTransaction(activity=activity, transaction=trans)
                    for trans in transactions
                ]
                ActivityTransaction.objects.bulk_create(activity_transactions)
            
            # Handle attachments
            for attachment in attachments:
                Attachment.objects.create(content_object=activity, file=attachment)
            
            return activity
            
    def update(self, instance, validated_data):
        transaction_ids = validated_data.pop('transaction_ids', None)
        
        with transaction.atomic():
            # Update the activity fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Process transactions if provided
            if transaction_ids is not None:
                # Get current transaction links
                current_links = instance.transaction_links.all()
                current_ids = set(str(link.transaction_id) for link in current_links)
                new_ids = set(str(tid) for tid in transaction_ids)
                
                # Find transactions to add and remove
                ids_to_remove = current_ids - new_ids
                ids_to_add = new_ids - current_ids
                
                # Remove unlinked transactions
                if ids_to_remove:
                    instance.transaction_links.filter(transaction_id__in=ids_to_remove).delete()
                
                # Add new transactions
                if ids_to_add:
                    # Get all valid transactions
                    organization = instance.organization
                    transactions = Transaction.objects.filter(
                        id__in=ids_to_add,
                        organization=organization,
                        type='disbursement'
                    )
                    
                    # Check for invalid transactions
                    valid_ids = set(str(t.id) for t in transactions)
                    invalid_ids = ids_to_add - valid_ids
                    
                    if invalid_ids:
                        raise serializers.ValidationError({
                            'transaction_ids': f"Invalid or non-disbursement transactions: {', '.join(invalid_ids)}"
                        })
                    
                    # Check for transactions already linked to other activities
                    linked_transactions = ActivityTransaction.objects.filter(
                        transaction_id__in=valid_ids
                    ).exclude(activity=instance).values_list('transaction_id', flat=True)
                    
                    if linked_transactions:
                        raise serializers.ValidationError({
                            'transaction_ids': f"Transactions already linked to other activities: {', '.join(str(tid) for tid in linked_transactions)}"
                        })
                    
                    # Create new activity transactions
                    activity_transactions = [
                        ActivityTransaction(activity=instance, transaction=trans)
                        for trans in transactions
                    ]
                    ActivityTransaction.objects.bulk_create(activity_transactions)
            
            return instance