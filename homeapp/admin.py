from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Branch)
admin.site.register(Deferred_Payment)
