from django.contrib import admin

from .models import BVHFile, BVHJob

admin.site.register(BVHJob)
admin.site.register(BVHFile)
