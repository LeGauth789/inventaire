from django.db import models
from django.contrib.auth.models import User

# Create your models here.

### Table de Produit ###
from django.db import models
from django.contrib.auth.models import User

class Produit(models.Model):
    
    nom = models.CharField("Nom du produit", max_length=200)
    condition_stock = models.CharField("Conditions de stockage", max_length=400, blank=True, default='')
    nb_FDS = models.PositiveIntegerField("Nombre de FDS", default=0)
    
    date_reception = models.DateField("Date de réception")
    fournisseur = models.CharField("Fournisseur", max_length=200)
    ref = models.CharField("Référence", max_length=200)
    nb_lot = models.CharField("Numéro de lot", max_length=200)
    
    stock = models.PositiveIntegerField("Stock", default=0)
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Utilisateur ayant ajouté"
    )

    fiche_pdf = models.FileField(upload_to='fichier_FDS/', null=True, blank=True)
    fichier_FDS = models.FileField(upload_to='fichier_FDS/', null=True, blank=True)
    fichier_CA = models.FileField(upload_to='fichier_CA/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.ref})"


### Table de Mouvement de stock ###
class MouvementStock(models.Model):

    AJOUT = 'AJOUT'
    RETRAIT = 'RETRAIT'

    TYPE_CHOICES = [
        (AJOUT, 'Ajout'),
        (RETRAIT, 'Retrait'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.PositiveIntegerField()
    date = models.DateTimeField(null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fournisseur = models.CharField(max_length=200, blank=True, null=True)  # facultatif pour les retraits
    commentaire = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.quantite} - {self.produit.nom} ({self.date})"