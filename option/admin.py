from django.contrib import admin
from .models import Option, SkipOption
# Register your models here.
admin.site.register(Option)
admin.site.register(SkipOption)