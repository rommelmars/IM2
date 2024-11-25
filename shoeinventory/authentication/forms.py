from django import forms
from .models import Shoe
from .models import Sale
from .models import Category

class ShoeForm(forms.ModelForm):
    class Meta:
        model = Shoe
        fields = ['name', 'brand', 'price', 'size', 'image', 'stock', 'category']  


class SaleForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label="Category",   
        empty_label="Select Category",
    )
    
    class Meta:
        model = Sale
        fields = ['shoe', 'quantity_sold']

    def clean(self):
        cleaned_data = super().clean()
        shoe = cleaned_data.get('shoe')
        category = cleaned_data.get('category')

        if shoe and category:
            if shoe.category != category:
                raise forms.ValidationError(
                    f"The selected shoe '{shoe.name}' does not belong to the category '{category.name}'."
                )
        return cleaned_data