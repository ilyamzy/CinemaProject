from django import forms


from .models import CinemaSession


class CinemaSessionAddForm(forms.ModelForm):
    class Meta:
        model = CinemaSession
        fields = ['movie', 'hall', 'start_time', 'single_seat_price', 'double_seat_price']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_movie(self):
        movie = self.cleaned_data.get('movie')
        if not movie:
            raise forms.ValidationError('Выберите фильм.')
        return movie

    def clean_hall(self):
        hall = self.cleaned_data.get('hall')
        if not hall:
            raise forms.ValidationError('Выберите зал.')
        return hall