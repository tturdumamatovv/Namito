from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from mptt.forms import TreeNodeChoiceField

from namito.catalog.models import (
    Category,
    Color,
    SizeChart,
    Tag,
    Product, Brand, Size
)


class CategoryAdminForm(forms.ModelForm):
    background_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Category
        fields = '__all__'


class ProductForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all())

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
        queryset=Category.objects.filter(parent__isnull=True),  # Только родительские категории
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Категории',
            is_stacked=False
        )
    )

    class Meta:
        model = Brand
        fields = '__all__'


class SizeForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Категории',
            is_stacked=False
        )
    )

    class Meta:
        model = Size
        fields = '__all__'
