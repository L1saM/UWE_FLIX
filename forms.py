from decimal import Clamped
from random import choices
from django import forms 
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CinemaControls, Film, Screen, Showing, Club


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def save(self, commit = True):
        user = super(SignUpForm, self).save(commit = False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

class LoginForm (forms.Form): 
    # Created 2 fields of a form 
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)

class FilmForm(ModelForm):
    class Meta:
        model = Film
        fields = ['title', 'description', 'duration', 'age_rating']

class ScreenForm(ModelForm):
    class Meta:
        model = Screen
        fields = ['capacity']

class ShowingForm(ModelForm):
    class Meta:
        model = Showing
        fields = ['showing_date', 'showing_time', 'film_id', 'screen_id']

class ClubForm(ModelForm):
    class Meta:
        model = Club
        fields = ['club_name', 'club_rep']

class DeleteFilmForm (forms.Form):

    def __init__(self, films, *args, **kwargs):
        super(DeleteFilmForm, self).__init__(*args, **kwargs)

        self.fields['film_id'] = forms.ChoiceField(choices=films)

class DeleteScreenForm (forms.Form):

    def __init__(self, screens, *args, **kwargs):
        super(DeleteScreenForm, self).__init__(*args, **kwargs)

        self.fields['screen_id'] = forms.ChoiceField(choices=screens)

class DeleteShowingForm (forms.Form):

    def __init__(self, showings, *args, **kwargs):
        super(DeleteShowingForm, self).__init__(*args, **kwargs)

        self.fields['showing_id'] = forms.ChoiceField(choices=showings)

class DeleteClubForm (forms.Form):

    def __init__(self, clubs, *args, **kwargs):
        super(DeleteClubForm, self).__init__(*args, **kwargs)

        self.fields['club_id'] = forms.ChoiceField(choices=clubs)

class AddCreditForm (forms.Form):
    credit = forms.DecimalField(max_digits=5, decimal_places=2)   

class BookingDateForm (forms.Form):

    def __init__(self, dates, *args, **kwargs):
        super(BookingDateForm, self).__init__(*args, **kwargs)

        self.fields['booking_date'] = forms.ChoiceField(choices=dates)

class BookingShowingsForm (forms.Form):

    def __init__(self, showings, *args, **kwargs):
        super(BookingShowingsForm, self).__init__(*args, **kwargs)

        self.fields['showing_id'] = forms.ChoiceField(choices=showings)

class BookingPaymentForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    card_num = forms.CharField(max_length=16)
    exp_date = forms.CharField(max_length=5)
    cvv = forms.CharField(max_length=3)

class ClubBookingDateForm(forms.Form):
    def __init__(self, dates, *args, **kwargs):
        super(ClubBookingDateForm, self).__init__(*args, **kwargs)

        self.fields['booking_date'] = forms.ChoiceField(choices=dates)

class CinemaControlsForm(ModelForm):
    class Meta:
        model = CinemaControls
        fields = ['club_discount', 'general_discount', 'covid_distancing']

class FindBookingForm(forms.Form):
    email = forms.EmailField(max_length=254)
    name = forms.CharField(max_length=30)

class DailyBookingsForm(forms.Form):
    booking_date = forms.DateField()

MONTH_CHOICES = (
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
)
class MonthlyBookingsForm(forms.Form):
    booking_month = forms.ChoiceField(choices=MONTH_CHOICES)