import django_filters
from .models import User, Item


class UserFilter(django_filters.FilterSet):  # Inherit from django_filters.FilterSet
    username = django_filters.CharFilter(lookup_expr="icontains", label="username")
    department = django_filters.AllValuesFilter(label="department")  # Exact match

    class Meta:
        model = User
        fields = ["username", "department"]


class ItemFilter(django_filters.FilterSet):
    item_name = django_filters.CharFilter(
        field_name="item_name", lookup_expr="icontains", label="Item Name"
    )

    paid_unpaid = django_filters.BooleanFilter(
        field_name="paid_unpaid",
        method="filter_paid_unpaid",
        label="Paid/Unpaid",
        required=False,
    )

    class Meta:
        model = Item
        fields = ["item_name", "paid_unpaid"]

    def filter_paid_unpaid(self, queryset, name, value):
        if value is not None:
            return queryset.filter(**{name: value})
        return queryset
