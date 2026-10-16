"""Workflow tests. Run:  python manage.py test"""
import json

from django.contrib.auth.models import User
from django.test import TestCase

from .models import CartItem, Order, Product


class ApiTestCase(TestCase):
    def setUp(self):
        self.keyboard = Product.objects.create(name="Mechanical Keyboard", description="RGB", price="3499.00", stock=15)
        self.mouse = Product.objects.create(name="Ergonomic Mouse", description="Vertical", price="1599.00", stock=3)

    def call(self, method, url, data=None):
        return getattr(self.client, method)(url, data=json.dumps(data or {}), content_type="application/json")

    def register(self, email="a@b.co", password="password1"):
        return self.call("post", "/api/auth/register/", {"email": email, "password": password})


class AuthTests(ApiTestCase):
    def test_register_login_logout_me(self):
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.client.get("/api/auth/me/").json()["user"]["email"], "a@b.co")
        self.call("post", "/api/auth/logout/")
        self.assertIsNone(self.client.get("/api/auth/me/").json()["user"])
        r = self.call("post", "/api/auth/login/", {"email": "a@b.co", "password": "password1"})
        self.assertEqual(r.status_code, 200)

    def test_duplicate_email(self):
        self.register()
        self.assertEqual(self.register().status_code, 409)

    def test_validation(self):
        self.assertEqual(self.register(password="short").status_code, 400)
        self.assertEqual(self.register(email="nope").status_code, 400)

    def test_wrong_password(self):
        self.register()
        self.call("post", "/api/auth/logout/")
        r = self.call("post", "/api/auth/login/", {"email": "a@b.co", "password": "wrongwrong"})
        self.assertEqual(r.status_code, 401)

    def test_cart_requires_login(self):
        self.assertEqual(self.client.get("/api/cart/").status_code, 401)
        self.assertEqual(self.call("post", "/api/checkout/").status_code, 401)


class ProductTests(ApiTestCase):
    def test_list_search_detail(self):
        self.assertEqual(len(self.client.get("/api/products/").json()["products"]), 2)
        found = self.client.get("/api/products/?q=keyboard").json()["products"]
        self.assertEqual([p["name"] for p in found], ["Mechanical Keyboard"])
        self.assertEqual(self.client.get(f"/api/products/{self.mouse.id}/").status_code, 200)
        self.assertEqual(self.client.get("/api/products/9999/").status_code, 404)


class CartTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.register()

    def add(self, product, quantity):
        return self.call("post", "/api/cart/", {"product_id": product.id, "quantity": quantity})

    def test_add_update_remove(self):
        self.assertEqual(self.add(self.keyboard, 2).json()["count"], 2)
        r = self.call("patch", f"/api/cart/{self.keyboard.id}/", {"quantity": 5})
        self.assertEqual(r.json()["count"], 5)
        r = self.call("delete", f"/api/cart/{self.keyboard.id}/")
        self.assertEqual(r.json()["count"], 0)

    def test_cannot_exceed_stock(self):
        self.assertEqual(self.add(self.mouse, 99).json()["items"][0]["quantity"], 3)

    def test_invalid_quantities(self):
        self.assertEqual(self.add(self.keyboard, -5).status_code, 400)
        self.assertEqual(self.add(self.keyboard, "abc").status_code, 400)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_unknown_and_out_of_stock_product(self):
        self.assertEqual(self.call("post", "/api/cart/", {"product_id": 9999, "quantity": 1}).status_code, 404)
        self.mouse.stock = 0
        self.mouse.save()
        self.assertEqual(self.add(self.mouse, 1).status_code, 409)

    def test_update_to_zero_removes_item(self):
        self.add(self.keyboard, 1)
        self.call("patch", f"/api/cart/{self.keyboard.id}/", {"quantity": 0})
        self.assertEqual(CartItem.objects.count(), 0)


class CheckoutTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.register()

    def test_checkout_creates_order_and_reduces_stock(self):
        self.call("post", "/api/cart/", {"product_id": self.mouse.id, "quantity": 2})
        r = self.call("post", "/api/checkout/")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["total"], "3198.00")
        self.mouse.refresh_from_db()
        self.assertEqual(self.mouse.stock, 1)
        self.assertEqual(CartItem.objects.count(), 0)
        self.assertEqual(len(self.client.get("/api/orders/").json()["orders"]), 1)

    def test_checkout_rolls_back_if_stock_vanished(self):
        self.call("post", "/api/cart/", {"product_id": self.mouse.id, "quantity": 3})
        Product.objects.filter(pk=self.mouse.pk).update(stock=1)
        r = self.call("post", "/api/checkout/")
        self.assertEqual(r.status_code, 409)
        self.assertIn("Not enough stock", r.json()["error"])
        self.assertEqual(Order.objects.count(), 0)
        self.mouse.refresh_from_db()
        self.assertEqual(self.mouse.stock, 1)

    def test_empty_checkout(self):
        self.assertEqual(self.call("post", "/api/checkout/").status_code, 409)

    def test_orders_are_private_per_user(self):
        self.call("post", "/api/cart/", {"product_id": self.keyboard.id, "quantity": 1})
        self.call("post", "/api/checkout/")
        self.call("post", "/api/auth/logout/")
        self.register(email="other@b.co")
        self.assertEqual(self.client.get("/api/orders/").json()["orders"], [])
        self.assertEqual(User.objects.count(), 2)
