
# Create your views here.
########################################
###               IMPORT             ###
########################################

from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import Produit ,MouvementStock


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from .forms import AjoutProduitForm , MouvementStockForm ,UploadPdfForm

from django.db.models import Q
from django.contrib.auth.models import User ,Group

########################################
########################################

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ajouter l'utilisateur dans un groupe par défaut (exemple "Employé")
            group, created = Group.objects.get_or_create(name='Employé')
            user.groups.add(group)
            messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'inventaire/register.html', {'form': form})

########################################
### Test Niveau D'acces Utilisateurs ###
########################################

def is_superuser(user):
    return user.is_superuser

def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_superuser

def is_employe(user):
    return user.groups.filter(name='Employe').exists()

########################################
########################################

########################################
###        GESTION DES DROITS        ###
########################################
#  Fonction qui gère l'affichage de l'interface administrateur

@user_passes_test(is_admin)
def gestion_droits(request):

    # Recuperation de toutes les instances Users et Groups de la BDD
    users = User.objects.all()
    groupes = Group.objects.all()


    if request.method == 'POST':
        user_id = request.POST.get('user')
        group_ids = request.POST.getlist('groups')

        try:
            user = User.objects.get(id=user_id)
            # Effacer tous les groupes actuels
            user.groups.clear()

            # Ajouter les groupes sélectionnés
            for gid in group_ids:
                groupe = Group.objects.get(id=gid)
                user.groups.add(groupe)
            user.save()
            messages.success(request, f"Droits mis à jour pour {user.username}")
        except User.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")

        return redirect('gestion_droits')

    return render(request, 'inventaire/gestion_droits.html', {
        'users': users,
        'groupes': groupes,
    })

########################################
########################################

########################################
###       GESTION BASE HTML          ###
########################################
# Permet d'afficher la base HTML/CSS/JS
#commune à toutes les pages

def base(request):
    return render(request, 'inventaire/base.html')

########################################
###      GESTION INVENTAIRE          ###
########################################

def liste_produits(request):
    sort = request.GET.get('sort', 'nom')
    order = request.GET.get('order', 'asc')

    produits = Produit.objects.all()

    if order == 'desc':
        produits = produits.order_by(f'-{sort}')
    else:
        produits = produits.order_by(sort)

    return render(request, 'inventaire/liste_produits.html', {
        'produits': produits,
        'current_sort': sort,
        'current_order': order
    })


def fiche_produit(request, pk):

    produit = get_object_or_404(Produit, pk=pk)
    mouvements = produit.mouvements.order_by('-date', '-id')  # récents en premier

    return render(request, 'inventaire/fiche_produit.html', {
        'produit': produit,
        'mouvements': mouvements,
    })


def ajouter_produit(request):
    if request.method == 'POST':

        if 'confirmer_ajout' in request.POST:
            nom = request.POST.get('nom')
            stock = int(request.POST.get('stock', 0))
            fournisseur = request.POST.get('fournisseur')
            date_reception = request.POST.get('date_reception')

            try:
                produit = Produit.objects.get(nom=nom)
            except Produit.DoesNotExist:
                messages.error(request, "Produit introuvable pour confirmation.")
                return redirect('ajouter_produit')

            produit.stock += stock
            produit.save()

            MouvementStock.objects.create(
                produit=produit,
                utilisateur=request.user,
                type_mouvement=MouvementStock.AJOUT,
                quantite=stock,
                fournisseur=fournisseur,
                commentaire="Ajout confirmé via formulaire"
            )

            messages.success(request, f"{stock} unités ajoutées au produit existant.")

            return redirect('fiche_produit', pk=produit.id)

        form = AjoutProduitForm(request.POST, request.FILES)
        if form.is_valid():

            nom = form.cleaned_data['nom']
            stock = form.cleaned_data['stock']
            date_reception = form.cleaned_data['date_reception']
            fournisseur = form.cleaned_data['fournisseur']

            try:
                produit = Produit.objects.get(nom=nom)

                # Produit existe déjà → confirmation nécessaire
                return render(request, 'inventaire/confirmer_ajout.html', {
                    'produit': produit,
                    'nom': nom,
                    'stock': stock,
                    'date_reception': date_reception,
                    'fournisseur': fournisseur,  # transmis au formulaire de confirmation
                })

            except Produit.DoesNotExist:

                # Création du nouveau produit
                nouveau_produit = form.save(commit=False)
                nouveau_produit.utilisateur = request.user

                nouveau_produit.save()

                MouvementStock.objects.create(
                    date = date_reception ,
                    produit=nouveau_produit,
                    utilisateur=request.user,
                    type_mouvement=MouvementStock.AJOUT,
                    quantite=stock,
                    fournisseur=fournisseur,
                    commentaire="Stock initial lors de la création du produit"
                )

                messages.success(request, "Produit ajouté avec succès.")

                return redirect('liste_produits')
    else:
        form = AjoutProduitForm()

    return render(request, 'inventaire/ajoutProduit.html', {'form': form})

def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = AjoutProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('fiche_produit', pk=produit.pk)
    else:
        form = AjoutProduitForm(instance=produit)
    return render(request, 'inventaire/modifier_produit.html', {'form': form})

def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        produit.delete()
        messages.success(request, f"Le produit '{produit.nom}' a été supprimé.")
        return redirect('liste_produits')

    return redirect('fiche_produit', pk=pk)

def gerer_mouvement_stock(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():

            date = form.cleaned_data['date']

            mouvement = form.save(commit=False)

            mouvement.date = date if date else timezone.now()
            mouvement.produit = produit

            mouvement.utilisateur = request.user
            print(date)
            mouvement.save()

            if mouvement.type_mouvement == MouvementStock.RETRAIT:
                if mouvement.quantite > produit.stock:
                    messages.error(request, "Stock insuffisant pour ce retrait.")
                    return redirect('gerer_mouvement_stock', produit_id=produit.id)
                produit.stock -= mouvement.quantite
            else:
                produit.stock += mouvement.quantite

            produit.save()
            mouvement.save()

            messages.success(request, "Mouvement de stock enregistré.")

            return redirect('fiche_produit', pk=produit.id)
    else:
        form = MouvementStockForm()

    return render(request, 'inventaire/gerer_mouvement.html', {
        'form': form,
        'produit': produit,
    })



def upload_pdf(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == 'POST':
        old_fds = produit.fichier_FDS
        old_ca = produit.fichier_CA

        form = UploadPdfForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()

            commentaire = []
            if 'fichier_FDS' in request.FILES and request.FILES['fichier_FDS'] != old_fds:
                commentaire.append("FDS mise à jour")
            if 'fichier_CA' in request.FILES and request.FILES['fichier_CA'] != old_ca:
                commentaire.append("Certificat d’analyse mis à jour")

            if commentaire:
                MouvementStock.objects.create(
                    date = timezone.now(),
                    produit=produit,
                    utilisateur=request.user,
                    type_mouvement="Modification",
                    quantite=0,
                    fournisseur="-",
                    commentaire=", ".join(commentaire)
                )

            messages.success(request, "Fichier PDF mis à jour avec succès.")
            return redirect('fiche_produit', pk=produit.pk)
    else:
        form = UploadPdfForm(instance=produit)

    return render(request, 'inventaire/upload_pdf.html', {
        'form': form,
        'produit': produit,
    })