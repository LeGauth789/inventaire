from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group

from .models import FicheProduit, LotProduit, MouvementStock
from .forms import  MouvementStockForm , LotProduitForm ,AjoutFicheLotForm , UploadFDSForm, UploadCAForm
from .utils import creer_mouvement_stock

# Auth
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group, _ = Group.objects.get_or_create(name='Employé')
            user.groups.add(group)
            messages.success(request, "Compte créé avec succès.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'inventaire/register.html', {'form': form})


# Group checks
def is_superuser(user):
    return user.is_superuser

def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_superuser

def is_employe(user):
    return user.groups.filter(name='Employe').exists()


@user_passes_test(is_admin)
def gestion_droits(request):
    users = User.objects.all()
    groupes = Group.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        group_ids = request.POST.getlist('groups')

        try:
            user = User.objects.get(id=user_id)
            user.groups.clear()
            for gid in group_ids:
                groupe = Group.objects.get(id=gid)
                user.groups.add(groupe)
            messages.success(request, f"Droits mis à jour pour {user.username}")
        except User.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")
        return redirect('gestion_droits')

    return render(request, 'inventaire/gestion_droits.html', {
        'users': users,
        'groupes': groupes,
    })


def base(request):
    return render(request, 'inventaire/base.html')


### INVENTAIRE

def liste_produits(request):
    # Champs autorisés pour le tri
    champs_tri_autorises = ['nom', 'ref', 'stock', 'nb_lot', 'fournisseur', 'date_reception']

    # Récupération des paramètres GET
    sort = request.GET.get('sort', 'nom')
    order = request.GET.get('order', 'asc')

    # Sécurisation du champ de tri
    if sort not in champs_tri_autorises:
        sort = 'nom'

    # Application du tri
    if order == 'desc':
        fiches_produit = FicheProduit.objects.all().order_by(f'-{sort}')
    else:
        fiches_produit = FicheProduit.objects.all().order_by(sort)

    return render(request, 'inventaire/liste_produits.html', {
        'fiches_produit': fiches_produit,
        'current_sort': sort,
        'current_order': order,
    })

def fiche_produit(request, pk):
    produit = get_object_or_404(FicheProduit, pk=pk)
    lots = produit.lots.all()
    return render(request, 'inventaire/fiche_produit.html', {
        'produit': produit,
        'lots': lots
    })

def ajouter_fiche_produit(request):
    if request.method == 'POST':
        form = AjoutFicheLotForm(request.POST, request.FILES)  # Pense à ajouter request.FILES pour les fichiers
        if form.is_valid():
            # Création fiche produit
            fiche = FicheProduit.objects.create(
                nom=form.cleaned_data['nom'],
                numero_fds=form.cleaned_data.get('numero_fds'),  # get() au cas où champ optionnel
                condition_stock=form.cleaned_data['condition_stock'],
                consigne_utilisation=form.cleaned_data['consigne_utilisation'],  # Attention au nom
                fichier_FDS=form.cleaned_data.get('fichier_FDS'),  # Respecte bien le nom exact du champ dans le modèle
            )
            # Création lot associé
            lot = LotProduit.objects.create(
                fiche_produit=fiche,
                nb_lot=form.cleaned_data['nb_lot'],
                ref=form.cleaned_data['ref'],
                date_reception=form.cleaned_data['date_reception'],
                stock_initial=form.cleaned_data['stock_initial'],
                fournisseur=form.cleaned_data['fournisseur'],
                fichier_CA=form.cleaned_data.get('fichier_CA'),
            )
            # Création mouvement stock initial
            creer_mouvement_stock(
                lot=lot,
                utilisateur=request.user,
                type_mouvement='AJOUT',
                quantite=form.cleaned_data['stock_initial'],
                commentaire="Stock initial à la création du lot"
            )
            messages.success(request, "Fiche produit, lot et mouvement de stock créés avec succès.")
            return redirect('liste_produits')
    else:
        form = AjoutFicheLotForm()
    return render(request, 'inventaire/ajouter_fiche_produit.html', {'form': form})


### Ajout d'un lot a une fiche ###
def ajouter_lot(request, pk):
    produit = get_object_or_404(FicheProduit, pk=pk)
    if request.method == 'POST':
        form = LotProduitForm(request.POST, request.FILES)
        if form.is_valid():
            lot = form.save(commit=False)
            lot.fiche_produit = produit
            lot.save()
            messages.success(request, "Lot ajouté avec succès.")
            return redirect('fiche_produit', pk=pk)
    else:
        form = LotProduitForm()
    return render(request, 'inventaire/ajouter_lot.html', {'form': form, 'produit': produit})

def gerer_mouvement_stock(request, pk):
    produit = get_object_or_404(FicheProduit, pk=pk)

    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.utilisateur = request.user
            mouvement.save()
            messages.success(request, "Mouvement enregistré avec succès.")
            return redirect('fiche_produit', pk=produit.pk)
    else:
        form = MouvementStockForm()
        # Filtrage des lots liés au produit si tu veux
        form.fields['lot'].queryset = LotProduit.objects.filter(fiche_produit=produit)

    return render(request, 'inventaire/gerer_mouvement_stock.html', {
        'form': form,
        'produit': produit
    })

def supprimer_fiche_produit(request, pk):
    fiche = get_object_or_404(FicheProduit, pk=pk)

    if request.method == 'POST':
        fiche.delete()
        messages.success(request, "Fiche produit supprimée avec succès.")
        return redirect('liste_produits')

    return render(request, 'inventaire/supprimer_fiche.html', {'fiche': fiche})

# def modifier_produit(request, pk):
#     fiche = get_object_or_404(FicheProduit, pk=pk)
#     if request.method == 'POST':
#         form = AjoutProduitForm(request.POST, request.FILES, instance=fiche)
#         if form.is_valid():
#             form.save()
#             return redirect('fiche_produit', pk=fiche.pk)
#     else:
#         form = AjoutProduitForm(instance=fiche)
#     return render(request, 'inventaire/modifier_produit.html', {'form': form})


def supprimer_produit(request, pk):
    fiche = get_object_or_404(FicheProduit, pk=pk)
    if request.method == "POST":
        fiche.delete()
        messages.success(request, f"Le produit '{fiche.nom}' a été supprimé.")
        return redirect('liste_produits')
    return redirect('fiche_produit', pk=pk)



def upload_fds(request, pk):
    fiche = get_object_or_404(FicheProduit, pk=pk)

    if request.method == 'POST':
        form = UploadFDSForm(request.POST, request.FILES, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "FDS mise à jour avec succès.")
            return redirect('fiche_produit', pk=pk)
    else:
        form = UploadFDSForm(instance=fiche)

    return render(request, 'inventaire/upload_fds.html', {'form': form, 'fiche': fiche})

def upload_ca(request, pk):
    lot = get_object_or_404(LotProduit, pk=pk)

    if request.method == 'POST':
        form = UploadCAForm(request.POST, request.FILES, instance=lot)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificat d’analyse mis à jour avec succès.")
            return redirect('fiche_produit', pk=lot.fiche_produit.pk)
    else:
        form = UploadCAForm(instance=lot)

    return render(request, 'inventaire/upload_ca.html', {'form': form, 'lot': lot})