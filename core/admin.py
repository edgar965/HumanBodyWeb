from django.contrib import admin
from .models import BVHJob, BVHFile

admin.site.register(BVHJob)
admin.site.register(BVHFile)
