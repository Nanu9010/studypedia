from django import forms
from django.contrib.auth import authenticate
from .models import User
import magic
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email.lower())
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise forms.ValidationError('No account found with this email.')
        else:
            user = authenticate(username=username_or_email, password=password)
            if user is None:
                raise forms.ValidationError('Invalid username or password.')

        if user is None or not user.is_active:
            raise forms.ValidationError('Invalid credentials or inactive account.')

        cleaned_data['user'] = user
        return cleaned_data


class SignUpForm(forms.ModelForm):
    password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name',
                  'college', 'year_of_study', 'location', 'phone', 'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email.lower()).exists():
            raise forms.ValidationError('This email is already in use.')
        return email.lower()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError({'password_confirm': 'Passwords must match.'})
        return cleaned_data

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(image.read(1024))
            if not file_type.startswith('image/'):
                raise ValidationError("Only image files are allowed.")
            if image.size > 2 * 1024 * 1024:  # 2MB limit
                raise ValidationError("Image size cannot exceed 2MB.")
            image.seek(0)
        return image


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'college', 'year_of_study', 'location', 'phone',
                  'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(image.read(1024))
            if not file_type.startswith('image/'):
                raise ValidationError("Only image files are allowed.")
            if image.size > 2 * 1024 * 1024:  # 2MB limit
                raise ValidationError("Image size cannot exceed 2MB.")
            image.seek(0)
        return image