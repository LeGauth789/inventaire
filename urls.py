from django.urls import path
from . import views
from .views import register

from django.contrib.auth import views as auth_views

urlpatterns = [

    path('base/', views.base, name='base'),

    path('admin/gestion-droits/', views.gestion_droits, name='gestion_droits'),

    path('login/', auth_views.LoginView.as_view(template_name='inventaire/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/<int:produit_id>/mouvement/', views.gerer_mouvement_stock, name='gerer_mouvement_stock'),
    path('produit/<int:pk>/upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('liste/', views.liste_produits, name='liste_produits'),
    path('produit/<int:pk>/', views.fiche_produit, name='fiche_produit'),
    path('produit/<int:pk>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produit/<int:pk>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    
]