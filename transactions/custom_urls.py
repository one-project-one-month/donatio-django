from django.urls import path
from .views import TransactionHistoryView

urlpatterns = [
    path("history/", TransactionHistoryView.as_view(), name="transaction-history"),
]
