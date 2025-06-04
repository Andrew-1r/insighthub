# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Dashboard, UserCSV, UserProfile
from allauth.socialaccount.forms import SignupForm

class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ['title']

class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = UserCSV
        fields = ['csv_title', 'csv_file']

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.lower().endswith('.csv'):
                raise forms.ValidationError("Only .csv files are allowed.")
        return file

