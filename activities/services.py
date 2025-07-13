from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from .models import Activity, ActivityTransaction
from organizations.models import Organization
from transactions.models import Transaction
from attachments.models import Attachment


def create_activity(
    org_admin_organization: Organization,
    title: str,
    description: str,
    location: str,
    disbursement_transaction_ids: list[int],
    uploaded_files: list = None,
) -> Activity:
    if uploaded_files is None:
        uploaded_files = []

    with db_transaction.atomic():
        valid_transactions = []
        for trans_id in disbursement_transaction_ids:
            try:
                trans = Transaction.objects.get(
                    id=trans_id, organization=org_admin_organization
                )

                if trans.transaction_type != "disbursement":
                    raise ValidationError(
                        f"Transaction {trans_id} is not a disbursement type."
                    )

                if ActivityTransaction.objects.filter(transaction=trans).exists():
                    raise ValidationError(
                        f"Transaction {trans_id} is already linked to another activity."
                    )

                valid_transactions.append(trans)
            except Transaction.DoesNotExist:
                raise ValidationError(
                    f"Transaction {trans_id} not found or does not belong to your organization."
                )

        activity = Activity.objects.create(
            organization=org_admin_organization,
            title=title,
            description=description,
            location=location,
        )

        for trans in valid_transactions:
            ActivityTransaction.objects.create(activity=activity, transaction=trans)

        activity_content_type = ContentType.objects.get_for_model(activity)
        for uploaded_file in uploaded_files:
            Attachment.objects.create(
                content_type=activity_content_type,
                object_id=activity.id,
                file=uploaded_file,
            )

    return activity


def edit_activity(
    org_admin_organization: Organization,
    activity_id: int,
    title: str = None,
    description: str = None,
    location: str = None,
    new_disbursement_transaction_ids: list[int] = None,
) -> Activity:
    if new_disbursement_transaction_ids is None:
        new_disbursement_transaction_ids = []

    with db_transaction.atomic():
        try:
            activity = Activity.objects.get(
                id=activity_id, organization=org_admin_organization
            )
        except Activity.DoesNotExist:
            raise ValidationError(
                f"Activity {activity_id} not found or does not belong to your organization."
            )

        if title is not None:
            activity.title = title
        if description is not None:
            activity.description = description
        if location is not None:
            activity.location = location
        activity.save()

        if new_disbursement_transaction_ids is not None:
            current_linked_activity_transactions = activity.transaction_links.all()
            current_linked_transaction_ids = {
                at.transaction.id for at in current_linked_activity_transactions
            }
            new_transaction_ids_set = set(new_disbursement_transaction_ids)

            for linked_at_obj in current_linked_activity_transactions:
                if linked_at_obj.transaction.id not in new_transaction_ids_set:
                    linked_at_obj.delete()

            for trans_id in new_transaction_ids_set:
                if trans_id not in current_linked_transaction_ids:
                    try:
                        trans = Transaction.objects.get(
                            id=trans_id, organization=org_admin_organization
                        )

                        if trans.transaction_type != "disbursement":
                            raise ValidationError(
                                f"New transaction {trans_id} is not a disbursement type."
                            )

                        if (
                            ActivityTransaction.objects.filter(transaction=trans)
                            .exclude(activity=activity)
                            .exists()
                        ):
                            raise ValidationError(
                                f"New transaction {trans_id} is already linked to another activity."
                            )

                        ActivityTransaction.objects.create(
                            activity=activity, transaction=trans
                        )

                    except Transaction.DoesNotExist:
                        raise ValidationError(
                            f"New transaction {trans_id} not found or does not belong to your organization."
                        )

    return activity
