import django_filters
from .models import User, Item, Order, OrderDetail
from django import forms


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


class OrderDetailFilter(django_filters.FilterSet):
    order_detail_id = django_filters.NumberFilter(
        field_name="order_detail_id", lookup_expr="exact", label="Order Detail ID"
    )
    order_id = django_filters.NumberFilter(
        field_name="order_id", lookup_expr="exact", label="Order ID"
    )
    username = django_filters.AllValuesFilter(
        field_name="customer__username", label="Username"
    )
    item_name = django_filters.ModelChoiceFilter(
        queryset=Item.objects.all(),
        field_name="item",
        label="Item Name",
        empty_label="All Items",
    )
    # Date range filter
    ordered_at = django_filters.DateFromToRangeFilter(
        field_name="ordered_at",
        label="Order Date Range",
        # widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = OrderDetail
        fields = ["order_detail_id", "order_id", "username", "item_name", "ordered_at"]
