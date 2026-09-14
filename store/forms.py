from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Product, Category, Profile, Color, Order, ProductImage, Province, District, Ward

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_percent', 'category', 'image', 'colors']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'colors': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['color', 'image']
        widgets = {
            'color': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên người nhận'})
    )
    
    phone_regex = RegexValidator(
        regex=r'^[0-9]+$',
        message="Số điện thoại chỉ được nhập số."
    )
    phone = forms.CharField(
        max_length=15, 
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Số điện thoại',
            'pattern': '[0-9]*',
            'title': 'Vui lòng chỉ nhập số'
        })
    )
    
    address = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ chi tiết (số nhà, tên đường...)'})
    )
    
    province = forms.CharField(required=False)
    district = forms.CharField(required=False)
    ward = forms.CharField(required=False)
    province_text = forms.CharField(required=False)
    district_text = forms.CharField(required=False)
    ward_text = forms.CharField(required=False)
    
    note = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú đơn hàng'})
    )
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        required=False,
        initial='cod',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )