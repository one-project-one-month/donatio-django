import django_filters
from .models import Transaction
from activities.models import ActivityTransaction

class TransactionFilter(django_filters.FilterSet):
    unlinked = django_filters.BooleanFilter(method='filter_unlinked')

    class Meta:
        model = Transaction
        fields = ['type', 'status', 'event', 'review_required']

    def filter_unlinked(self, queryset, name, value):
        if value:
            return queryset.filter(activity_links__isnull=True)
        return queryset
