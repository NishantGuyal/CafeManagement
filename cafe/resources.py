from .models import User, Item
from import_export import resources, fields


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = (
            "username",
            "department",
        )


class ItemResource(resources.ModelResource):

    class Meta:
        model = Item
        fields = ("item_name", "paid_unpaid")
