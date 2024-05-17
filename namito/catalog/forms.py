from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from namito.catalog.models import (
    Category,
    Color,
    SizeChart,
    Tag,
    Product, Brand
)


class CategoryAdminForm(forms.ModelForm):
    background_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Category
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'tag': FilteredSelectMultiple("Tags", is_stacked=False),
        }


class ColorAdminForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Color
        fields = '__all__'


class TagAdminForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = '__all__'


class SizeChartForm(forms.ModelForm):
    class Meta:
        model = SizeChart
        fields = '__all__'
        widgets = {
            'categories': FilteredSelectMultiple("Categories", is_stacked=False),
        }


class BrandForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Категории',
            is_stacked=False
        )
    )

    class Meta:
        model = Brand
        fields = '__all__'
