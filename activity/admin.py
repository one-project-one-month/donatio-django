from django.contrib import admin
from .models import Activity, ActivityTransaction

# Register your models here.
admin.site.register(Activity)
admin.site.register(ActivityTransaction)