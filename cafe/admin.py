from django.contrib import admin
from django.utils.timezone import now
from .models import User, Item, Order, OrderDetail


class UserAdmin(admin.ModelAdmin):
    list_display = (
        # "user_id",
        "username",
        "department",
        "created_at",
        "updated_at",
        "is_active",
    )

    fieldsets = (
        ("Basic Info", {"fields": ("username", "department")}),
        (
            "Others",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "deleted_at")
    search_fields = ("username", "department")
    list_filter = ("department",)
    actions = ["soft_delete_users", "restore_users"]

    def is_active(self, obj):
        return "Active" if obj.deleted_at is None else "Inactive"

    is_active.short_description = "Active Status"

    def delete_model(self, request, obj):
        obj.deleted_at = now()
        obj.save()

    def soft_delete_users(self, request, queryset):
        queryset.update(deleted_at=now())

    soft_delete_users.short_description = "Soft delete selected users"

    def restore_users(self, request, queryset):
        queryset.update(deleted_at=None)

    restore_users.short_description = "Restore selected users"


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        # "item_id",
        "item_name",
        "paid_unpaid",
        "created_at",
        "updated_at",
        "is_active",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    search_fields = ("item_name",)
    list_filter = ("paid_unpaid", "created_at")
    actions = ["soft_delete_users", "restore_users"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Basic Info", {"fields": ("item_name", "paid_unpaid")}),
        (
            "Others",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def is_active(self, obj):
        return "Active" if obj.deleted_at is None else "Inactive"

    is_active.short_description = "Active Status"

    def is_active(self, obj):
        return "Active" if obj.deleted_at is None else "Inactive"

    is_active.short_description = "Active Status"

    def delete_model(self, request, obj):
        obj.deleted_at = now()
        obj.save()

    def soft_delete_items(self, request, queryset):
        queryset.update(deleted_at=now())

    soft_delete_items.short_description = "Soft delete selected items"

    def restore_items(self, request, queryset):
        queryset.update(deleted_at=None)

    restore_items.short_description = "Restore selected items"


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1
    fields = ("customer", "item", "counter")
    readonly_fields = ("ordered_at",)
    can_delete = True


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDetailInline]
    list_display = ("order_id", "created_at", "updated_at")


class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ("order", "item", "customer", "counter", "ordered_at", "updated_at")


admin.site.register(User, UserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)

admin.site.site_header = "Cafe Admin"
admin.site.index_title = "Welcome to Cafe Admin Panel"
