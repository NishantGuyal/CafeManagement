from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils.timezone import now
from django.contrib import messages
from .models import Order, Item, User, OrderDetail
from django.http import HttpResponse
from django.db.models import Sum


def index(request):
    if not request.user.is_authenticated:
        return redirect("admin_login")

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


def user_management(request):
    users = User.objects.filter(deleted_at__isnull=True)
    return render(request, "users.html", {"users": users})


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


def item_list(request):
    items = Item.objects.filter(deleted_at__isnull=True)
    return render(request, "items.html", {"items": items})


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


def order_management(request):
    users = User.objects.filter(deleted_at__isnull=True)
    items = Item.objects.filter(deleted_at__isnull=True)
    return render(request, "orders.html", {"users": users, "items": items})


def create_order(request):
    if request.method == "POST":
        # Create a new order entry in the Order table
        order = Order.objects.create(created_at=now(), updated_at=now())

        # Get the form data from the POST request
        customers = request.POST.getlist("customer")
        items = request.POST.getlist("item")
        counters = request.POST.getlist("counter")

        # Loop through the customers, items, and counters to create corresponding OrderDetail entries
        for customer_id, item_id, counter in zip(customers, items, counters):
            # Ensure counter is an integer and defaults to 0 if empty
            counter = int(counter) if counter else 0

            # Create the order details for each mini order
            OrderDetail.objects.create(
                order=order,
                customer_id=customer_id,
                item_id=item_id,
                counter=counter,
                ordered_at=now(),
                updated_at=now(),
            )

        # After saving the order and its details, redirect to the main order page
        return redirect("order_management")  # Redirect to the order management page

    else:
        return HttpResponse("Invalid request method", status=405)


def order_report(request):
    # Fetch orders along with the sum of counter from order_details
    orders = Order.objects.annotate(
        total_quantity=Sum("order_details__counter")
    ).filter(deleted_at__isnull=True)

    # Render the template and pass the orders with their total quantity
    return render(request, "order_report.html", {"orders": orders})

def order_delete(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    # Update the `deleted_at` field for the order and its corresponding order details
    deleted_at = now()

    # Update Order
    order.deleted_at = deleted_at
    order.save()

    # Update OrderDetails
    order_details = OrderDetail.objects.filter(order=order)
    for order_detail in order_details:
        order_detail.deleted_at = deleted_at
        order_detail.save()

    # Redirect to the order management page or order list
    return redirect('order_report')  # Replace 'order_management' with your actual URL name