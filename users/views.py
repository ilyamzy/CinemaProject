from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import CreateView, FormView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, AddManagerForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')


class AddManager(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = AddManagerForm
    template_name = 'users/add_manager.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            form.add_error('username', 'Пользователь не найден.')
            return self.form_invalid(form)

        if user.role != 'user':
            form.add_error('username', f'Вы не можете изменить роль пользователя {username}')
            return self.form_invalid(form)

        user.role = 'manager'
        user.save()

        messages.success(self.request, f'Роль пользователя {username} успешно изменена на "manager".')
        return redirect(self.get_success_url())

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {
        'title': "Профиль пользователя",
    }

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user