# ShopEasy – E-Commerce Web Application (Django + React)

Full-stack e-commerce app: **Django** REST-style JSON API + **React (Vite)** frontend.

## Features
- User authentication (register, login, logout) with Django sessions and CSRF protection
- Product listing with search, stock badges
- Shopping cart: add / update / remove, quantities capped at available stock
- Atomic checkout (transaction) that re-checks stock, creates an order and reduces inventory
- Order history per user
- Reusable React components: `ProductCard`, `CartItem`, `AuthForm`, `Navbar`, `Message`, `ProtectedRoute`
- Django ORM models: `Product`, `CartItem`, `Order`, `OrderItem`

## Project structure
```
backend/            Django project
  config/           settings, root urls
  store/            models, views (API), urls, tests, seed command
frontend/           React app (Vite)
  src/api.js        one fetch wrapper for the whole API
  src/context/      AuthContext, CartContext (global state)
  src/components/   reusable UI
  src/pages/        Products, Login, Register, Cart, Orders
```

## Setup

### 1. Backend (terminal 1)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py makemigrations store
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```

### 2. Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**. Vite proxies `/api` to Django on port 8000.

### 3. Run tests
```bash
cd backend
python manage.py test
```

## API endpoints
| Method | URL | Purpose | Auth |
|---|---|---|---|
| GET | `/api/csrf/` | set CSRF cookie | – |
| POST | `/api/auth/register/` | create account | – |
| POST | `/api/auth/login/` | log in | – |
| POST | `/api/auth/logout/` | log out | yes |
| GET | `/api/auth/me/` | current user | – |
| GET | `/api/products/?q=` | list / search products | – |
| GET | `/api/products/<id>/` | product detail | – |
| GET | `/api/cart/` | view cart | yes |
| POST | `/api/cart/` | add `{product_id, quantity}` | yes |
| PATCH | `/api/cart/<product_id>/` | set `{quantity}` (0 removes) | yes |
| DELETE | `/api/cart/<product_id>/` | remove item | yes |
| POST | `/api/checkout/` | place order | yes |
| GET | `/api/orders/` | order history | yes |

## Bugs found and fixed while testing workflows
| Issue | Fix |
|---|---|
| Cart quantity could exceed stock | Capped at stock in add/update |
| Negative / non-numeric quantity accepted | Validated, returns 400 |
| Checkout could oversell if stock changed | `transaction.atomic()` + stock re-check + rollback |
| Duplicate registration crashed | Returns 409 with clear message |
| Unauthenticated cart/checkout access | `api_login_required` returns 401 |
| Stale cart after failed checkout | Frontend refreshes cart to show current stock |
