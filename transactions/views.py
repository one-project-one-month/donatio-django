from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer, UpdateTransactionSerializer
from .constants import TransactionType
from rest_framework.permissions import IsAuthenticated


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    # filterset_fields = ['organization', 'donor', 'event', 'type', 'status', 'review_required']
    # search_fields = ['donor__name', 'event__title']
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UpdateTransactionSerializer
        return TransactionSerializer

    def get_queryset(self):
        # Get the organization from the URL
        organization_pk = self.kwargs.get("organization_id")
        if organization_pk:
            return self.queryset.filter(organization_pk=organization_pk)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            donor=self.request.user,
            type=TransactionType.DISBURSEMENT,
        )

    # @action(detail=False, methods=['post'], url_path='donate', serializer_class=TransactionSerializer)
    # def donate_to_organization(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(organization=request.user.organization, donor=request.user, type=TransactionType.DONATION)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=False, methods=['post'], url_path='donate', serializer_class=TransactionSerializer)
    # def donate_to_event(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(organization=request.user.organization, donor=request.user, type=TransactionType.DONATION, event=kwargs['event_id'])
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
