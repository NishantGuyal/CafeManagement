import django_tables2 as tables
from .models import User, Item, OrderDetail
from django.db.models import Sum

class UserTable(tables.Table):
    username = tables.Column(verbose_name="User Name")
    department = tables.Column(verbose_name="Department")
    created_at = tables.DateTimeColumn(format="d M Y, H:i")
    updated_at = tables.DateTimeColumn(format="d M Y, H:i")
    deleted_at = tables.DateTimeColumn(format="d M Y, H:i", empty_values=())

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap4.html"
        exclude = ("user_id",)


class ItemTable(tables.Table):
    item_name = tables.Column(verbose_name="Item Name")
    paid_unpaid = tables.Column(verbose_name="Paid Status")
    created_at = tables.DateTimeColumn(format="d M Y, H:i")
    updated_at = tables.DateTimeColumn(format="d M Y, H:i")
    deleted_at = tables.DateTimeColumn(format="d M Y, H:i", empty_values=())

    class Meta:
        model = Item
        template_name = "django_tables2/bootstrap4.html"
        exclude = ("item_id",)


class OrderTable(tables.Table):
    order_detail_id = tables.Column(verbose_name="Order Detail ID")
    user = tables.Column(accessor="user.username", verbose_name="User")
    item = tables.Column(accessor="item.item_name", verbose_name="Item")
    counter = tables.Column(verbose_name="Counter")
    ordered_at = tables.DateTimeColumn(format="d M Y, H:i")
    updated_at = tables.DateTimeColumn(format="d M Y, H:i")
    deleted_at = tables.DateTimeColumn(format="d M Y, H:i", empty_values=())

    class Meta:
        model = OrderDetail
        template_name = "django_tables2/bootstrap4.html"
        exclude = ("deleted_at", "user")

    @property
    def total_counter(self):
        """Calculate the total count of the 'counter' column"""
        return OrderDetail.objects.aggregate(Sum("counter"))["counter__sum"]
