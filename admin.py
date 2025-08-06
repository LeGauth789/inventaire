from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Produit, MouvementStock

# Register your models here.

admin.site.register(Produit)
admin.site.register(MouvementStock)

