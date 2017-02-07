from django.utils.http import is_safe_url
from .forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.core.urlresolvers import reverse_lazy

from .forms import RegistrationForm



class LoginView(FormView):
    """Login using username and password
    Author: Amr Draz
    """
    success_url = '/'
    form_class = AuthenticationForm
    redirect_field_name = 'next'
    template_name = 'accounts/login.html'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.POST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class LogoutView(RedirectView):
    """Logout and redirect to /
    Author: Amr Draz
    """
    url = '/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class RegistrationView(FormView):
    """Register using username, email, password
    Author: Amr Draz
    """
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """If the form is valid, create user and redirect to the supplied URL.
        """
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return super(RegistrationView, self).form_valid(form)
