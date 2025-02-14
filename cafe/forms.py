from django import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class UserFilterForm(forms.Form):
    username = forms.CharField(max_length=255, required=False, label="username")
    department = forms.CharField(max_length=255, required=False, label="department")


class ItemFilterForm(forms.Form):
    item_name = forms.CharField(max_length=255, required=False, label="Item Name")
    paid_unpaid = forms.MultipleChoiceField(
        choices=[(True, "Paid"), (False, "Unpaid")],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
