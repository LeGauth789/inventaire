from django.utils import timezone
from .models import MouvementStock

def creer_mouvement_stock(lot, utilisateur, type_mouvement, quantite, fournisseur=None, commentaire=None, date=None):
    if date is None:
        date = timezone.now()
    mouvement = MouvementStock.objects.create(
        lot=lot,
        utilisateur=utilisateur,
        type_mouvement=type_mouvement,
        quantite=quantite,
        fournisseur=fournisseur or '',
        commentaire=commentaire or '',
        date=date
    )
    return mouvement