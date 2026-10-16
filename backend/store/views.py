"""REST-style JSON API: auth, products, cart, checkout, orders."""
import json
from decimal import Decimal
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from .models import CartItem, Order, OrderItem, Product


class CheckoutError(Exception):
    pass


# ---------------------------------------------------------------- helpers
def error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def json_body(request):
    """Parse a JSON body; return {} for empty/invalid input instead of crashing."""
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def to_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def api_login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return error("Authentication required.", 401)
        return view(request, *args, **kwargs)
    return wrapped


def serialize_user(user):
    return {"id": user.id, "email": user.username}


def serialize_product(p):
    return {"id": p.id, "name": p.name, "description": p.description,
            "price": str(p.price), "stock": p.stock}


def serialize_cart(user):
    items = CartItem.objects.filter(user=user).select_related("product").order_by("product__name")
    rows, total, count = [], Decimal("0"), 0
    for it in items:
        line = it.product.price * it.quantity
        total += line
        count += it.quantity
        rows.append({"product_id": it.product_id, "name": it.product.name,
                     "price": str(it.product.price), "stock": it.product.stock,
                     "quantity": it.quantity, "line_total": str(line)})
    return {"items": rows, "total": str(total), "count": count}


def serialize_order(order):
    return {
        "id": order.id,
        "total": str(order.total),
        "created_at": order.created_at.isoformat(),
        "items": [{"name": i.name, "unit_price": str(i.unit_price), "quantity": i.quantity}
                  for i in order.items.all()],
    }


# ------------------------------------------------------------------- auth
@ensure_csrf_cookie
@require_http_methods(["GET"])
def csrf(request):
    return JsonResponse({"ok": True})


@require_POST
def register(request):
    data = json_body(request)
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    try:
        validate_email(email)
    except ValidationError:
        return error("Enter a valid email address.")
    if len(password) < 8:
        return error("Password must be at least 8 characters.")
    if User.objects.filter(username=email).exists():
        return error("That email is already registered.", 409)
    user = User.objects.create_user(username=email, email=email, password=password)
    login(request, user)
    return JsonResponse({"user": serialize_user(user)}, status=201)


@require_POST
def login_view(request):
    data = json_body(request)
    email = str(data.get("email", "")).strip().lower()
    user = authenticate(request, username=email, password=str(data.get("password", "")))
    if user is None:
        return error("Incorrect email or password.", 401)
    login(request, user)
    return JsonResponse({"user": serialize_user(user)})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def me(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": serialize_user(request.user)})
    return JsonResponse({"user": None})


# --------------------------------------------------------------- products
@require_http_methods(["GET"])
def product_list(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.all()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return JsonResponse({"products": [serialize_product(p) for p in products]})


@require_http_methods(["GET"])
def product_detail(request, product_id):
    try:
        return JsonResponse(serialize_product(Product.objects.get(pk=product_id)))
    except Product.DoesNotExist:
        return error("Product not found.", 404)


# ------------------------------------------------------------------- cart
@api_login_required
@require_http_methods(["GET", "POST"])
def cart_collection(request):
    if request.method == "GET":
        return JsonResponse(serialize_cart(request.user))

    data = json_body(request)
    qty = to_int(data.get("quantity", 1))
    if qty is None or qty < 1:
        return error("Quantity must be a whole number of at least 1.")
    try:
        product = Product.objects.get(pk=to_int(data.get("product_id"), 0))
    except Product.DoesNotExist:
        return error("Product not found.", 404)
    if product.stock < 1:
        return error("This product is out of stock.", 409)

    item, _ = CartItem.objects.get_or_create(user=request.user, product=product,
                                             defaults={"quantity": 0})
    item.quantity = min(item.quantity + qty, product.stock)  # never exceed stock
    item.save()
    return JsonResponse(serialize_cart(request.user), status=201)


@api_login_required
@require_http_methods(["PATCH", "DELETE"])
def cart_item(request, product_id):
    item = CartItem.objects.filter(user=request.user, product_id=product_id).select_related("product").first()
    if item is None:
        return error("Item not in cart.", 404)
    if request.method == "DELETE":
        item.delete()
    else:
        qty = to_int(json_body(request).get("quantity"))
        if qty is None:
            return error("Quantity must be a whole number.")
        if qty <= 0:
            item.delete()
        else:
            item.quantity = min(qty, item.product.stock)
            item.save()
    return JsonResponse(serialize_cart(request.user))


# --------------------------------------------------------------- checkout
@api_login_required
@require_POST
def checkout(request):
    """Turn the cart into an order atomically; stock is re-checked inside the transaction."""
    try:
        with transaction.atomic():
            items = list(CartItem.objects.select_for_update().filter(user=request.user))
            if not items:
                raise CheckoutError("Your cart is empty.")
            order = Order.objects.create(user=request.user)
            total = Decimal("0")
            for it in items:
                product = Product.objects.select_for_update().get(pk=it.product_id)
                if it.quantity > product.stock:
                    raise CheckoutError(
                        f"Not enough stock for {product.name} (only {product.stock} left).")
                OrderItem.objects.create(order=order, product=product, name=product.name,
                                         unit_price=product.price, quantity=it.quantity)
                product.stock -= it.quantity
                product.save(update_fields=["stock"])
                total += product.price * it.quantity
            order.total = total
            order.save(update_fields=["total"])
            CartItem.objects.filter(user=request.user).delete()
    except CheckoutError as exc:
        return error(str(exc), 409)  # transaction rolled back automatically
    return JsonResponse(serialize_order(order), status=201)


@api_login_required
@require_http_methods(["GET"])
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return JsonResponse({"orders": [serialize_order(o) for o in orders]})
