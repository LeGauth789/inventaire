from django.contrib import admin
from django.contrib.auth.models import Group

from .models import FicheProduit, LotProduit, MouvementStock

# Register your models here.

admin.site.register(FicheProduit)
admin.site.register(LotProduit)
admin.site.register(MouvementStock)

