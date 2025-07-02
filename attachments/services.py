from attachments.models import Attachment


def delete_attachment_by_object_id(object_id: str):
    """
    Delete all attachments by object id
    """
    try:
        Attachment.objects.filter(object_id=object_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting attachments: {e}")
        return False
