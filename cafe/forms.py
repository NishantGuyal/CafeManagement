from django import forms
from .models import OrderDetail, User, Item


class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = ["customer", "item", "counter"]
        widgets = {
            "counter": forms.NumberInput(attrs={"value": "0", "min": "0", "step": "1"}),
        }

    customer = forms.ModelChoiceField(queryset=User.objects.all(), label="User")
    item = forms.ModelChoiceField(queryset=Item.objects.all(), label="Item")
