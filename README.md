# Smart Cart
A modern, feature-rich desktop shopping cart application built with Python and Tkinter. Smart Cart delivers a seamless e-commerce experience with user authentication, a curated product catalog, persistent cart management, and an advanced coupon system-including a daily lucky draw. The app supports robust checkout with form validation and stores user and coupon data securely via CSV files.

## Features
- User registration and login with password strength checks
- Persistent user, cart, and coupon data (CSV-backed)
- Modern, responsive UI with themed widgets
- Product catalog with quantity selection and real-time cart summary
- Apply default and daily lucky draw coupons (with one-per-user-per-day logic)
- Checkout with address and payment form validation (credit/debit card or UPI)

## Coupon system
- Default Coupons: Apply codes like WELCOME10 (10% off), FREESHIP (₹500 off shipping), or BIGSPENDER (20% off orders over ₹50,000).
- Daily Lucky Draw: Spin once per day for a chance to win a unique coupon.
- Coupons are tracked per user and cannot be reused.

## Installation
### 1. Clone the repository
```
git clone https://github.com/KausLol/Smart-Cart.git
cd Smart-Cart
```

### 2. Install dependencies
Make sure you have Python 3.8 or higher installed.
```
pip install -r requirements.txt
```

### 3. Run the program
```
python smartcart.py
```
