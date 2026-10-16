from django.urls import path
from . import views

urlpatterns = [
    path("csrf/", views.csrf),
    path("auth/register/", views.register),
    path("auth/login/", views.login_view),
    path("auth/logout/", views.logout_view),
    path("auth/me/", views.me),
    path("products/", views.product_list),
    path("products/<int:product_id>/", views.product_detail),
    path("cart/", views.cart_collection),
    path("cart/<int:product_id>/", views.cart_item),
    path("checkout/", views.checkout),
    path("orders/", views.order_list),
]
