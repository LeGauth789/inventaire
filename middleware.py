from django.shortcuts import redirect
from django.urls import reverse


########################################
###      GESTION Connexion           ###
########################################
#Ce middleware permet de verifier sur l'utilisateur est connecté à
#son compte avant de le rediriger vers une page
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ne bloque pas les pages de login, admin, etc.
        allowed_paths = [reverse('register'),reverse('login'), reverse('admin:login')]

        if not request.user.is_authenticated and request.path not in allowed_paths: 
            return redirect('login')

        return self.get_response(request)
