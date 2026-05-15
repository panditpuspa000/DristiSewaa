from django import forms  # Fixed: added 's' to forms
from .models import Branch, User

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['branch_name', 'location', 'manager']
        widgets = {
            'branch_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter Branch Name'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter Location'}),
            'manager': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users with the 'manager' role in the dropdown
        # This ensures administrative integrity as per your project requirements
        self.fields['manager'].queryset = User.objects.filter(role='manager')