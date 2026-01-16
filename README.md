# ecom-backend

A Django REST Framework-based e-commerce backend API with JWT authentication, product management, shopping cart, orders, and reviews.

## Setup Instructions

### 1. Create Virtual Environment

Navigate to the project root directory (`ecom-backend`) and create a virtual environment:

```bash
cd ecom-backend
python -m venv venv
```

### 2. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

Navigate to the backend directory and run migrations:

```bash
cd backend
python manage.py migrate
```

### 5. Create Superuser (Optional)

Create an admin user to access Django admin panel:

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Features & Functionality

### 1. **User Authentication (AuthUser)**
- **User Registration**: Create new user accounts with username, email, password, phone number, and address
- **User Login**: Authenticate users and receive JWT tokens (stored in HttpOnly cookies and response body)
- **User Logout**: Logout users by blacklisting refresh tokens and deleting authentication cookies
- **User Profile**: View and update authenticated user's profile information
- **JWT Authentication**: Secure token-based authentication using `djangorestframework-simplejwt`

### 2. **Product Management (Products)**
- **Product Listing**: List all available products
- **Product Details**: View and update product information
- **Product Features**:
  - Product name, description, and price
  - Stock management
  - Product images (using Pillow)
  - Availability status
  - Single product e-commerce support

### 3. **Shopping Cart (Cart)**
- **Add to Cart**: Add products to user's shopping cart
- **View Cart**: List all items in the authenticated user's cart
- **Update Cart**: Modify cart item quantities
- **Remove from Cart**: Delete items from cart
- **Quantity Management**: Increase or decrease item quantities
- **Automatic Price Calculation**: Total price calculated based on product price and quantity

### 4. **Order Management (Order)**
- **Create Orders**: Place new orders with product, quantity, and shipping address
- **Order Listing**: View all orders for authenticated user
- **Order Details**: View and update specific order information
- **Order Status Tracking**: Track orders through different statuses:
  - Pending
  - Processing
  - Shipped
  - Delivered
  - Cancelled
- **Stock Management**: Automatically updates product stock when orders are placed
- **Price Calculation**: Automatic total price calculation based on product price and quantity

### 5. **Product Reviews (Review)**
- **Create Reviews**: Authenticated users can create product reviews with ratings (1-5 stars) and comments
- **View Reviews**: Anyone can view product reviews (filterable by product)
- **Update Reviews**: Users can update their own reviews
- **Delete Reviews**: Users can delete their own reviews (admins can delete any review)
- **One Review Per User**: Each user can only have one review per product (enforced by unique constraint)

## API Documentation

The project uses `drf-yasg` for Swagger/OpenAPI documentation. Once the server is running, access the API documentation at:

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

## Technology Stack

- **Django 5.2.8**: Web framework
- **Django REST Framework 3.16.1**: REST API framework
- **djangorestframework-simplejwt 5.3.1**: JWT authentication
- **django-cors-headers 4.9.0**: CORS handling
- **drf-yasg 1.21.7**: API documentation
- **Pillow 12.0.0**: Image processing

## Project Structure

```
ecom-backend/
├── backend/
│   ├── AuthUser/          # User authentication and management
│   ├── Products/          # Product management
│   ├── Cart/              # Shopping cart functionality
│   ├── Order/             # Order management
│   ├── Review/            # Product reviews
│   └── backend/           # Django project settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Notes

- All authentication endpoints use JWT tokens stored in HttpOnly cookies for enhanced security
- Cart and Order operations require user authentication
- Product and Review listings are publicly accessible, but creating reviews requires authentication
- The project is configured for single product e-commerce but can be extended for multiple products
