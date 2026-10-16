# Resume wording + Git plan

## Project entry (use this)
**E-Commerce Web Application** | Django, React, REST APIs, SQLite, Git
- Built user authentication (register/login/logout) and a persistent shopping cart using Django and REST-style JSON APIs.
- Developed a React frontend with reusable components (product card, cart item, auth form) and context-based state management.
- Designed database models with the Django ORM and implemented transactional checkout that validates stock to prevent overselling.
- Tested user workflows (signup → add to cart → checkout) and fixed bugs including stock-limit violations, invalid quantities and duplicate registrations.

## Short version (if space is tight)
- Developed a full-stack e-commerce app with Django REST-style APIs and a React frontend, covering authentication, cart and checkout.
- Tested user workflows and fixed bugs in cart quantity handling, stock validation and registration.

## Skills section (matches this project)
- **Languages:** C, Python, Java (basic)
- **Web:** HTML, CSS, JavaScript, React
- **Framework:** Django (basic)
- **CS fundamentals:** DSA, OOP, DBMS, Operating Systems
- **Tools & concepts:** REST APIs, Backend Development, Git, GitHub, SDLC fundamentals
- **Testing:** Debugging, manual workflow testing, basic Django unit tests

## Suggested Git commit history
```
git init
git add .gitignore README.md && git commit -m "Initial commit: project README and gitignore"
git add backend/config backend/manage.py backend/requirements.txt && git commit -m "Set up Django project and settings"
git add backend/store/models.py backend/store/admin.py && git commit -m "Add Product, CartItem, Order models"
git add backend/store/views.py backend/store/urls.py && git commit -m "Add auth, product, cart and checkout API"
git add backend/store/tests.py && git commit -m "Add workflow tests for auth, cart and checkout"
git add frontend && git commit -m "Add React frontend with reusable components"
git commit --allow-empty -m "Fix: cap cart quantity at stock and validate input"
```
Create a repo on GitHub, then: `git remote add origin <url>` and `git push -u origin main`.

## Interview talking points (be ready to explain these)
1. **Why session auth + CSRF?** Browser app on one origin (via Vite proxy); Django sessions are built in and secure.
2. **Why `transaction.atomic()` at checkout?** Two users could buy the last item; stock is re-checked inside the transaction and everything rolls back on failure.
3. **Why store `OrderItem.name` and `unit_price`?** Orders must keep the price paid even if the product changes later.
4. **Why Context in React?** Auth and cart state are needed by many components (Navbar, ProductCard, Cart).
5. **What would you add next?** Payments, product images, pagination, JWT or DRF, deployment.

> Be honest about scope: the API uses plain Django views returning JSON (not Django REST Framework). Say that confidently - it shows you understand what DRF does under the hood.
