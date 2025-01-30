from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User
from django.http import HttpResponse


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
    users = User.objects.all()
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
    user.delete()
    return redirect("user_management")


# View to update a user
def update_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    if request.method == "POST":
        user.username = request.POST["username"]
        user.department = request.POST["department"]
        user.save()
        return redirect("user_management")

    return HttpResponse("Invalid request", status=400)
