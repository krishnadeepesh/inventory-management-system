from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Category, Product, PurchaseRequest, FeedbackMessage

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = 'USER' # Only users can signup
        if commit:
            user.save()
        return user

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter for active categories
        queryset = Category.objects.filter(is_active=True)
        
        # If editing an existing product, include its current category even if inactive
        if self.instance and self.instance.pk and self.instance.category:
            queryset = queryset | Category.objects.filter(pk=self.instance.category.pk)
            
        self.fields['category'].queryset = queryset.distinct()

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['quantity']

class FeedbackMessageForm(forms.ModelForm):
    class Meta:
        model = FeedbackMessage
        fields = ['content']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
