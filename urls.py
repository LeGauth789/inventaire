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

    path('liste/', views.liste_produits, name='liste_produits'),
    path('fiche/<int:pk>/', views.fiche_produit, name='fiche_produit'),
    path('fiche/<int:pk>/ajouter_lot/', views.ajouter_lot, name='ajouter_lot'),
    path('fiche/<int:pk>/mouvement_stock/', views.gerer_mouvement_stock, name='gerer_mouvement_stock'),

    path('fiche/<int:pk>/supprimer/', views.supprimer_fiche_produit, name='supprimer_fiche_produit'),

    path('ajouter/', views.ajouter_fiche_produit, name='ajouter_fiche_produit'),

    path('fiche/<int:pk>/upload_fds/', views.upload_fds, name='upload_fds'),
    path('lot/<int:pk>/upload_ca/', views.upload_ca, name='upload_ca'),
    

]