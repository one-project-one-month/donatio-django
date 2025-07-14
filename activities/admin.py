from django.contrib import admin
from .models import Activity, ActivityTransaction

admin.site.register(Activity)
admin.site.register(ActivityTransaction)