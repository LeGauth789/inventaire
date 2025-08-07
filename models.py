from django.db import models
from django.contrib.auth.models import User


### 1. Fiche Produit – Définition générique du produit
class FicheProduit(models.Model):

    nom = models.CharField("Nom du produit", max_length=200)
    numero_fds = models.CharField("Numéro FDS", max_length=100)
    condition_stock = models.TextField("Conditions de stockage", blank=True)
    consigne_utilisation = models.TextField("Consignes d'utilisation", blank=True)

    fichier_FDS = models.FileField("Fichier FDS (PDF)", upload_to='fichier_FDS/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} (FDS: {self.numero_fds})"


### 2. Lot Produit – Une réception physique d’un produit
class LotProduit(models.Model):

    fiche_produit = models.ForeignKey(FicheProduit, on_delete=models.CASCADE, related_name="lots")
    nb_lot = models.CharField("Numéro de lot", max_length=100)
    ref = models.CharField("ref", max_length=100)
    date_reception = models.DateField("Date de réception")
    fournisseur = models.CharField("Fournisseur", max_length=200)

    stock_initial = models.PositiveIntegerField("Quantité reçue")

    fichier_CA = models.FileField("Certificat d’analyse (PDF)", upload_to='fichier_CA/', null=True, blank=True)

    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.fiche_produit.nom} – Lot {self.nb_lot}"

    @property
    def quantite_actuelle(self):
        entrees = self.mouvements.filter(type_mouvement='AJOUT').aggregate(models.Sum('quantite'))['quantite__sum'] or 0
        retraits = self.mouvements.filter(type_mouvement='RETRAIT').aggregate(models.Sum('quantite'))['quantite__sum'] or 0
        return self.stock_initial + entrees - retraits


### 3. Mouvement de Stock – Entrée ou sortie de stock pour un lot
class MouvementStock(models.Model):

    AJOUT = 'AJOUT'
    RETRAIT = 'RETRAIT'

    TYPE_CHOICES = [
        (AJOUT, 'Ajout'),
        (RETRAIT, 'Retrait'),
    ]

    lot = models.ForeignKey(LotProduit, on_delete=models.CASCADE, related_name="mouvements")
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    fournisseur = models.CharField(max_length=200, blank=True, null=True)

    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_mouvement_display()} de {self.quantite} – {self.lot}"
