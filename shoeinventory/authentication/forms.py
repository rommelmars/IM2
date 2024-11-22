from django import forms
from .models import Shoe
from .models import Sale

class ShoeForm(forms.ModelForm):
    class Meta:
        model = Shoe
        fields = ['name', 'brand', 'price', 'size', 'image', 'stock', 'category']  


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['shoe', 'quantity_sold']