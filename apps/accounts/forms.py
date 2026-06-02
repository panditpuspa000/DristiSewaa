from django import forms
from .models import User, Branch, ManagerProfile, FrontDeskProfile

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['branch_name', 'location', 'email', 'manager']
        widgets = {
            'branch_name': forms.TextInput(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
            'location': forms.TextInput(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
            'email': forms.EmailInput(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
            'manager': forms.Select(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
        }

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        # Replaces the standard '---------' placeholder with a clean label text context
        if 'manager' in self.fields:
            self.fields['manager'].empty_label = "Select an available manager account..."

class AdminManagerCreationForm(forms.ModelForm):
    # Form password input matching user interface styling guidelines
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'id': 'drawerPassword',
        'style': 'width: 100%; box-sizing: border-box; padding: 12px 44px 12px 44px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b; outline: none;'
    }))
    
    # Selection menu allowing admins to declare management vs front desk tier roles
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('staff', 'Front Desk / Staff')],
        widget=forms.Select(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'})
    )
    
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        widget=forms.Select(attrs={'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'})
    )
    
    experience_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'e.g. rthapa', 'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Rohit', 'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Thapa', 'style': 'width: 100%; box-sizing: border-box; padding: 12px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b;'}),
        }

    def __init__(self, *args, **kwargs):
        super(AdminManagerCreationForm, self).__init__(*args, **kwargs)
        # Strips out the standard selection spacer characters cleanly
        if 'branch' in self.fields:
            self.fields['branch'].empty_label = "Select a branch location..."

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Enforce the selected drop-down choice into the base User database row instance
        selected_role = self.cleaned_data.get('role', 'staff')
        user.role = selected_role
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            target_branch = self.cleaned_data.get('branch')
            
            # Dynamic Profile Mapper System Routing Check
            if selected_role == 'manager':
                ManagerProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'branch': target_branch,
                        'experience_details': self.cleaned_data.get('experience_details')
                    }
                )
            else:
                FrontDeskProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'branch': target_branch
                    }
                )
        return user