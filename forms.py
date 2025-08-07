from django import forms
from .models import FicheProduit, LotProduit, MouvementStock

class FicheProduitForm(forms.ModelForm):
    class Meta:
        model = FicheProduit
        fields = ['nom', 'condition_stock', 'consigne_utilisation', 'fichier_FDS']
        widgets = {
            'condition_stock': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'consigne_utilisation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LotProduitForm(forms.ModelForm):
    class Meta:
        model = LotProduit
        fields = ['ref', 'nb_lot', 'date_reception', 'fournisseur', 'stock_initial', 'fichier_CA']
        widgets = {
            'date_reception': forms.DateInput(attrs={'type': 'date'}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'ref': forms.TextInput(attrs={'class': 'form-control'}),
            'nb_lot': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_initial': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class MouvementStockForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )

    class Meta:
        model = MouvementStock
        fields = ['lot', 'type_mouvement', 'quantite', 'fournisseur', 'commentaire']
        widgets = {
            'lot': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fournisseur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fournisseur (optionnel)'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Commentaire (optionnel)'}),
        }

class AjoutFicheLotForm(forms.Form):
    # Champs fiche produit
    nom = forms.CharField(max_length=200)
    numero_fds = forms.IntegerField(min_value=1)
    condition_stock = forms.CharField(max_length=100)
    consigne_utilisation = forms.CharField(max_length=100)

    fichier_FDS = forms.FileField()

    # Champs lot
    date_reception = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    ref = forms.CharField(max_length=100)
    fournisseur = forms.CharField(max_length=200)
    nb_lot = forms.CharField(max_length=100)
    stock_initial = forms.IntegerField(min_value=0)
    
    fichier_CA = forms.FileField()
    
    

class UploadFDSForm(forms.ModelForm):
    class Meta:
        model = FicheProduit
        fields = ['fichier_FDS']

class UploadCAForm(forms.ModelForm):
    class Meta:
        model = LotProduit
        fields = ['fichier_CA']
