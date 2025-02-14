from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
import datetime
from django_tables2.config import RequestConfig
from django.utils.dateparse import parse_date
import csv
from .models import Order, Item, User, OrderDetail
from .resources import UserResource, ItemResource
from .forms import CsvImportForm
from .filters import ItemFilter, UserFilter, OrderDetailFilter
from .tables import UserTable, ItemTable, OrderTable
import json


@login_required
def index(request):
    customer_ids = request.GET.getlist("customer")
    item_ids = request.GET.getlist("item")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if "" in customer_ids:
        customer_ids = [user.user_id for user in User.objects.all()]
    if "" in item_ids:
        item_ids = [item.item_id for item in Item.objects.all()]

    queryset = OrderDetail.objects.filter(deleted_at__isnull=True)

    if customer_ids:
        queryset = queryset.filter(customer_id__in=customer_ids)
    if item_ids:
        queryset = queryset.filter(item_id__in=item_ids)
    if start_date:
        queryset = queryset.filter(ordered_at__date__gte=parse_date(start_date))
    if end_date:
        queryset = queryset.filter(ordered_at__date__lte=parse_date(end_date))

    data = queryset.values("customer__username", "item__item_name").annotate(
        total_quantity=Sum("counter")
    )

    chart_data = {}
    for entry in data:
        customer = entry["customer__username"]
        item = entry["item__item_name"]
        qty = entry["total_quantity"]

        if customer not in chart_data:
            chart_data[customer] = {}
        chart_data[customer][item] = qty

    customers = list(chart_data.keys())
    items = set()
    datasets = []

    for customer, item_data in chart_data.items():
        for item, qty in item_data.items():
            items.add(item)

    items = list(items)

    colors = [
        "rgba(255, 99, 132, 0.5)",  # Red
        "rgba(54, 162, 235, 0.5)",  # Blue
        "rgba(255, 206, 86, 0.5)",  # Yellow
        "rgba(75, 192, 192, 0.5)",  # Green
        "rgba(153, 102, 255, 0.5)",  # Purple
        "rgba(255, 159, 64, 0.5)",  # Orange
        "rgba(255, 99, 71, 0.5)",  # Tomato
        "rgba(0, 255, 255, 0.5)",  # Cyan
        "rgba(255, 20, 147, 0.5)",  # DeepPink
        "rgba(34, 193, 195, 0.5)",  # Aqua
        "rgba(253, 187, 45, 0.5)",  # Mustard
        "rgba(204, 51, 255, 0.5)",  # Violet
        "rgba(128, 128, 0, 0.5)",  # Olive
        "rgba(255, 69, 0, 0.5)",  # Red-Orange
        "rgba(144, 238, 144, 0.5)",  # LightGreen
        "rgba(135, 206, 250, 0.5)",  # LightSkyBlue
        "rgba(238, 130, 238, 0.5)",  # Violet
        "rgba(64, 224, 208, 0.5)",  # Turquoise
        "rgba(255, 105, 180, 0.5)",  # HotPink
    ]

    for idx, item in enumerate(items):
        dataset = {
            "label": item,
            "data": [chart_data[customer].get(item, 0) for customer in customers],
            "backgroundColor": colors[idx % len(colors)],
            "borderColor": colors[idx % len(colors)].replace("0.5", "1"),
            "borderWidth": 1,
        }
        datasets.append(dataset)

    item_data = queryset.values("item__item_name").annotate(
        total_quantity=Sum("counter")
    )

    item_chart_data = {}
    for entry in item_data:
        item = entry["item__item_name"]
        qty = entry["total_quantity"]
        item_chart_data[item] = qty

    items_chart = list(item_chart_data.keys())
    items_chart_quantities = list(item_chart_data.values())

    context = {
        "customers": User.objects.all(),
        "items": Item.objects.all(),
        "customers_labels": json.dumps(customers),
        "datasets": json.dumps(datasets),
        "items_for_second_chart": json.dumps(items_chart),
        "quantities_for_items": json.dumps(items_chart_quantities),
    }

    return render(request, "index.html", context)


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


def user_table(request):
    table = UserTable(User.objects.all())
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    return render(request, "user_table.html", {"table": table})


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


def item_table(request):
    table = ItemTable(Item.objects.all())
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    return render(request, "item_table.html", {"table": table})


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


def order_table(request):
    orders = OrderDetail.objects.filter(deleted_at__isnull=True)

    order_filter = OrderDetailFilter(request.GET, queryset=orders)
    table = OrderTable(order_filter.qs)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    return render(request, "order_table.html", {"table": table, "filter": order_filter})
