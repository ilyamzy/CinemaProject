from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
        required=True,
    )
    phone_number = forms.CharField(
        label='Номер телефона',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=True,
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email


class AddManagerForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = ['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'manager'
        if commit:
            user.save()
        return user


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'password'
        ]


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
    )
    email = forms.EmailField(
        disabled=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )
    phone_number = forms.CharField(
        label='Номер телефона',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'phone_number',
            'first_name',
            'last_name'
        ]
