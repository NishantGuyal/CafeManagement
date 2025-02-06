from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
import datetime
from django.utils.dateparse import parse_date
import csv
from .models import Order, Item, User, OrderDetail
from .resources import UserResource, ItemResource
from .forms import CsvImportForm
from .filters import ItemFilter, UserFilter


@login_required
def index(request):
    return render(request, "index.html")


def admin_login(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, "admin_login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


def user_management(request):
    users = User.objects.filter(deleted_at__isnull=True)
    filterset = UserFilter(request.GET, queryset=users)
    return render(
        request, "users.html", {"users": filterset.qs, "filterset": filterset}
    )


def create_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        department = request.POST.get("department")

        User.objects.create(username=username, department=department)

        return redirect("user_management")

    return redirect("user_management")


def remove_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    user.deleted_at = now()
    user.save()
    return redirect("user_management")


def update_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    if request.method == "POST":
        user.username = request.POST["username"]
        user.department = request.POST["department"]
        user.save()
        return redirect("user_management")

    return HttpResponse("Invalid request", status=400)


@login_required
def user_export(request):
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if not start_date or not end_date:
        return HttpResponse("Invalid date range", status=400)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    if not start_date or not end_date:
        return HttpResponse("Invalid date format", status=400)

    end_date = datetime.datetime.combine(end_date, datetime.time.max)

    users = User.objects.filter(created_at__range=[start_date, end_date])

    resource = UserResource()
    dataset = resource.export(users)

    response = HttpResponse(dataset.csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users_export.csv"'

    return response


@login_required
def user_import(request):
    if request.method == "POST" and request.FILES["csv_file"]:
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            return HttpResponse("Only CSV files are allowed.")

        dataset = csv_file.read().decode("utf-8")
        imported_data = dataset.splitlines()
        reader = csv.reader(imported_data)

        next(reader)

        for row in reader:
            if len(row) < 2:
                continue

            username = row[0]
            department = row[1]

            current_time = now()

            deleted_at = None
            user = User(
                username=username,
                department=department,
                created_at=current_time,
                updated_at=current_time,
                deleted_at=deleted_at,
            )

            user.save()

        return HttpResponse("Data imported successfully!")

    form = CsvImportForm()
    return render(request, "import_csv.html", {"form": form})


@login_required
def item_list(request):
    items = Item.objects.filter(deleted_at__isnull=True)
    item_filter = ItemFilter(request.GET, queryset=items)

    return render(
        request, "items.html", {"items": item_filter.qs, "filter": item_filter}
    )


def create_item(request):
    if request.method == "POST":
        item_name = request.POST["item_name"]
        paid_unpaid = request.POST["paid_unpaid"] == "true"
        Item.objects.create(item_name=item_name, paid_unpaid=paid_unpaid)
        return redirect("item_list")


def update_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":
        item.item_name = request.POST["item_name"]
        item.paid_unpaid = request.POST["paid_unpaid"] == "true"
        item.save()
        return redirect("item_list")


def remove_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":
        item.deleted_at = now()
        item.save()
        return redirect("item_list")


@login_required
def item_export(request):
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if not start_date or not end_date:
        return HttpResponse("Invalid date range", status=400)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    if not start_date or not end_date:
        return HttpResponse("Invalid date format", status=400)

    end_date = datetime.datetime.combine(end_date, datetime.time.max)

    items = Item.objects.filter(created_at__range=[start_date, end_date])

    resource = ItemResource()
    dataset = resource.export(items)

    response = HttpResponse(dataset.csv, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="items_export.csv"'

    return response


@login_required
def item_import(request):
    if request.method == "POST" and request.FILES["csv_file"]:
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            return HttpResponse("Only CSV files are allowed.")

        dataset = csv_file.read().decode("utf-8")
        imported_data = dataset.splitlines()
        reader = csv.reader(imported_data)

        next(reader)

        for row in reader:
            if len(row) < 2:
                continue

            item_name = row[0]
            paid_unpaid = row[1]

            current_time = now()

            deleted_at = None
            item = Item(
                item_name=item_name,
                paid_unpaid=paid_unpaid,
                created_at=current_time,
                updated_at=current_time,
                deleted_at=deleted_at,
            )

            item.save()

        return HttpResponse("Data imported successfully!")

    form = CsvImportForm()
    return render(request, "import_csv.html", {"form": form})


@login_required
def order_management(request):
    users = User.objects.filter(deleted_at__isnull=True)
    items = Item.objects.filter(deleted_at__isnull=True)
    return render(request, "orders.html", {"users": users, "items": items})


def create_order(request):
    if request.method == "POST":
        order = Order.objects.create(created_at=now(), updated_at=now())

        customers = request.POST.getlist("customer")
        items = request.POST.getlist("item")
        counters = request.POST.getlist("counter")

        for customer_id, item_id, counter in zip(customers, items, counters):
            counter = int(counter) if counter else 1

            OrderDetail.objects.create(
                order=order,
                customer_id=customer_id,
                item_id=item_id,
                counter=counter,
                ordered_at=now(),
                updated_at=now(),
            )

        return redirect("order_report")

    else:
        return HttpResponse("Invalid request method", status=405)


@login_required
def order_report(request):
    orders = Order.objects.annotate(
        total_quantity=Sum(
            "order_details__counter",
            filter=Q(order_details__deleted_at__isnull=True),
        )
    ).filter(deleted_at__isnull=True)

    return render(request, "order_report.html", {"orders": orders})


def order_delete(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    deleted_at = now()

    order.deleted_at = deleted_at
    order.save()

    order_details = OrderDetail.objects.filter(order=order)
    for order_detail in order_details:
        order_detail.deleted_at = deleted_at
        order_detail.save()

    return redirect("order_report")


def update_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_details = OrderDetail.objects.filter(order=order, deleted_at__isnull=True)

    users = User.objects.filter(deleted_at__isnull=True)
    items = Item.objects.filter(deleted_at__isnull=True)

    if request.method == "POST":
        changes_made = False

        submitted_order_details = request.POST.getlist("order_detail_id[]")
        for order_detail_id in submitted_order_details:
            order_detail = OrderDetail.objects.get(order_detail_id=order_detail_id)

            new_customer_id = request.POST.get(f"customer_{order_detail_id}")
            new_item_id = request.POST.get(f"item_{order_detail_id}")
            new_counter = request.POST.get(f"counter_{order_detail_id}")

            if (
                str(order_detail.customer_id) != new_customer_id
                or str(order_detail.item_id) != new_item_id
                or str(order_detail.counter) != new_counter
            ):
                order_detail.customer_id = new_customer_id
                order_detail.item_id = new_item_id
                order_detail.counter = new_counter
                order_detail.updated_at = now()
                order_detail.save()
                changes_made = True

        new_customers = request.POST.getlist("new_customer[]")
        new_items = request.POST.getlist("new_item[]")
        new_counters = request.POST.getlist("new_counter[]")
        for i in range(len(new_customers)):
            if new_customers[i] and new_items[i] and new_counters[i]:
                OrderDetail.objects.create(
                    order=order,
                    customer_id=new_customers[i],
                    item_id=new_items[i],
                    counter=new_counters[i],
                    updated_at=now(),
                )
                changes_made = True

        deleted_order_detail_ids = request.POST.getlist("deleted_order_details[]")
        deleted_order_detail_ids = [
            int(id) for id in deleted_order_detail_ids if id.isdigit()
        ]

        for deleted_id in deleted_order_detail_ids:
            if deleted_id:
                OrderDetail.objects.filter(order_detail_id=deleted_id).update(
                    deleted_at=now()
                )
                changes_made = True

        if changes_made:
            order.updated_at = now()
            order.save()

        return redirect("order_report")

    return render(
        request,
        "update_order.html",
        {
            "order": order,
            "order_details": order_details,
            "users": users,
            "items": items,
        },
    )
