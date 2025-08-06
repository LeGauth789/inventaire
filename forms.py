from django import forms
from .models import Produit , MouvementStock

class AjoutProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom','condition_stock','nb_FDS', 'date_reception','fournisseur','ref',
                  'nb_lot','stock', 'fichier_FDS']
        widgets = {
            'date_reception': forms.DateInput(attrs={'type': 'date'})
        }


class MouvementStockForm(forms.ModelForm):
     
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )

    class Meta:
        model = MouvementStock
        fields = ['type_mouvement', 'quantite', 'fournisseur', 'commentaire']
        widgets = {
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fournisseur (optionnel)'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire (optionnel)'}),
        }

class UploadPdfForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['fichier_FDS','fichier_CA']