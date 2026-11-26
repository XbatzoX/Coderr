# Coderr Backend API

A modular RESTful backend built with **Django** and **Django REST Framework (DRF)** for **Coderr**, a freelance marketplace connecting customers with business service providers.

The API supports role-based authentication (`customer` and `business` accounts), user profiles, tiered service offers (`basic`, `standard`, `premium`), order lifecycle management, business profile reviews, platform-wide statistics, and request throttling.

---

## Tech Stack

- **Backend:** Python 3, Django, Django REST Framework
- **Authentication:** DRF Token Authentication
- **Filtering & Pagination:** `django-filter`, DRF Search/Ordering Filters, PageNumberPagination
- **Database:** SQLite (default development setup)
- **Testing:** Django `APITestCase` & `unittest.mock` (84 automated tests)

---

## Project Structure

```text
Coderr/
├── base_info_app/      # Aggregated platform statistics endpoint (/api/base-info/)
├── core/               # Project settings, root URL routing, and throttling configuration
├── offers_app/         # Service offers and tiered packages (basic, standard, premium)
├── orders_app/         # Order creation, status tracking, and business order counters
├── Postman/            # Exported Postman collection and environment files
├── profile_app/        # User profiles with automatic creation via Django signals
├── reviews_app/        # Business profile ratings, reviews, and filtering
├── user_auth_app/      # CustomUser model, registration, and token login
├── manage.py
└── requirements.txt
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/XbatzoX/Coderr.git
cd Coderr
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell / CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0`.

---

## Running Automated Tests

The project includes **84 unit and integration tests** covering authentication, permissions, filtering, validation, rate limiting, and error handling across all apps.

Run the full test suite with:

```bash
python manage.py test
```

---

## Postman Collection & Environment

Ready-to-use Postman files are included in the [`Postman/`](https://github.com) directory for manual endpoint testing:

1. Open **Postman** and click **Import** in the top-left corner.
2. Select and import both the collection file and the environment file from the `Postman/` folder.
3. Select the imported **Coderr** environment in the top-right dropdown of Postman.
4. Run the **Login** or **Registration** request first to obtain an authentication token, and set the `token` environment variable for authenticated endpoints (`Authorization: Token <your_token>`).

---

## API Endpoints Overview

### Authentication (`user_auth_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/registration/` | Register a new `customer` or `business` user | Public (`auth` throttle) |
| `POST` | `/api/login/` | Authenticate user and retrieve API token | Public (`auth` throttle) |

### Profiles (`profile_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/profile/{pk}/` | Retrieve a user's profile details | Authenticated |
| `PATCH` | `/api/profile/{pk}/` | Update own profile details and email | Profile Owner |
| `GET` | `/api/profiles/business/` | List all business user profiles | Authenticated |
| `GET` | `/api/profiles/customer/` | List all customer user profiles | Authenticated |

### Offers (`offers_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/offers/` | List paginated offers (supports search, ordering, filters) | Public |
| `POST` | `/api/offers/` | Create an offer with `basic`, `standard`, and `premium` tiers | Business User |
| `GET` | `/api/offers/{id}/` | Retrieve full details for a specific offer | Authenticated |
| `PATCH` | `/api/offers/{id}/` | Update an existing offer and its tiers | Offer Owner |
| `DELETE` | `/api/offers/{id}/` | Delete an offer | Offer Owner |
| `GET` | `/api/offerdetails/{id}/` | Retrieve a single offer package detail | Authenticated |

### Orders (`orders_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/orders/` | List all orders associated with the current user | Authenticated |
| `POST` | `/api/orders/` | Create an order from an `offer_detail_id` | Customer User |
| `PATCH` | `/api/orders/{id}/` | Update order status (`in_progress`, `completed`, `cancelled`) | Assigned Business User |
| `GET` | `/api/order-count/{business_user_id}/` | Count active (`in_progress`) orders for a business user | Authenticated |
| `GET` | `/api/completed-order-count/{business_user_id}/` | Count `completed` orders for a business user | Authenticated |

### Reviews (`reviews_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/reviews/` | List reviews (supports `business_user_id`, `reviewer_id`, ordering) | Authenticated |
| `POST` | `/api/reviews/` | Create a review (max. 1 review per business profile) | Customer User |
| `PATCH` | `/api/reviews/{id}/` | Update rating or description of an existing review | Review Author |
| `DELETE` | `/api/reviews/{id}/` | Delete a review | Review Author |

### Platform Info (`base_info_app`)

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/base-info/` | Retrieve review count, average rating, business count, and offer count | Public |

---

## Rate Limiting (Throttling)

To protect the API against brute-force attacks and excessive traffic, Django REST Framework throttling is enabled:
- **Anonymous users (`anon`):** `60/minute`
- **Authenticated users (`user`):** `120/minute`
- **Authentication endpoints (`auth` scope on `/api/login/` & `/api/registration/`):** `10/minute`
