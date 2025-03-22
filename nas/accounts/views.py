from django.shortcuts import redirect
from django.contrib.auth import views
from .forms import AuthenticationFormWithBS


class LoginViewCustom(views.LoginView):
    form_class = AuthenticationFormWithBS
    template_name = 'registration/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main')
        return super().dispatch(request, *args, **kwargs)
