import tkinter as tk
from tkinter import ttk, messagebox
import random
import datetime
import csv
import os
import re  
from PIL import Image, ImageTk, ImageDraw  

class EnhancedShoppingCart:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Cart")
        self.root.geometry("1400x900")  
        
        try:
            icon = Image.open('shopping-cart.png')
            icon = icon.resize((32, 32))
            icon_tk = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, icon_tk)
        except Exception as e:
            print(f"Could not set window icon: {str(e)}")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure modern colors and styles
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 12))
        self.style.configure("TButton", 
                           font=("Segoe UI", 12),
                           padding=15,
                           background="#003366",  
                           foreground="white")
        self.style.configure("TLabelframe", 
                           background="#f0f0f0",
                           font=("Segoe UI", 13, "bold"))
        self.style.configure("TLabelframe.Label", 
                           background="#f0f0f0",
                           font=("Segoe UI", 13, "bold"))
        self.style.configure("TEntry", 
                           padding=8,
                           font=("Segoe UI", 12))
        self.style.configure("TSpinbox", 
                           padding=5,
                           font=("Segoe UI", 10))
        
        self.style.map("TButton",
                      background=[("active", "#002244")],  
                      foreground=[("active", "white")])
        
        self.currency_symbol = '₹'

        # CSV-based user storage
        self.users_file = 'users.csv'
        self.daily_coupons_file = 'daily_coupons.csv'
        self.used_coupons_file = 'used_coupons.csv'
        self.users = self.load_users()
        self.daily_coupons = self.load_daily_coupons()
        self.used_coupons = self.load_used_coupons()
        self.logged_in_user = None

        # Updated product catalog with more items and realistic prices
        self.products = {
            "MacBook Pro M3": {"price": 199999, "category": "Electronics", "description": "16-inch, 18GB RAM, 512GB SSD"},
            "iPhone 15 Pro Max": {"price": 149999, "category": "Electronics", "description": "256GB, Titanium"},
            "Sony WH-1000XM5": {"price": 34999, "category": "Audio", "description": "Wireless Noise Cancelling Headphones"},
            "Canon EOS R5": {"price": 289999, "category": "Photography", "description": "45MP Full-Frame Mirrorless Camera"},
            "Apple Watch Series 9": {"price": 45999, "category": "Wearables", "description": "GPS, 45mm, Aluminum"},
            "Logitech MX Master 3S": {"price": 9999, "category": "Accessories", "description": "Wireless Mouse"},
            "Samsung 65\" QLED 4K": {"price": 189999, "category": "Electronics", "description": "Smart TV with HDR"},
            "Bose QuietComfort Ultra": {"price": 32999, "category": "Audio", "description": "Wireless Earbuds"},
            "DJI Mini 3 Pro": {"price": 89999, "category": "Photography", "description": "4K Drone with Camera"},
            "iPad Pro 12.9\"": {"price": 99999, "category": "Electronics", "description": "M2 Chip, 256GB"}
        }

        self.base_coupons = {
            "WELCOME10": {"type": "percentage", "value": 0.10, "min_amount": 0},
            "FREESHIP": {"type": "fixed", "value": 500, "min_amount": 0},
            "BIGSPENDER": {"type": "percentage", "value": 0.20, "min_amount": 50000}
        }
        self.applied_coupons = []
        self.cart = {}

        self.create_auth_interface()

    # ------------------ USER STORAGE ------------------
    def load_users(self):
        users = {}
        if os.path.exists(self.users_file):
            with open(self.users_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        username, password = row
                        users[username] = password
        else:
            users = {"premium_user": "secure123", "guest": "guest123"}
            with open(self.users_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                for username, password in users.items():
                    writer.writerow([username, password])
        return users

    def save_users(self):
        with open(self.users_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for username, password in self.users.items():
                writer.writerow([username, password])

    # ------------------ DAILY COUPON STORAGE ------------------
    def load_daily_coupons(self):
        daily = {}
        if os.path.exists(self.daily_coupons_file):
            with open(self.daily_coupons_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 6:
                        username, date_str, code, ctype, cvalue, cmin = row
                        daily[username] = {
                            "date": date_str,
                            "coupon": {
                                "code": code,
                                "type": ctype,
                                "value": float(cvalue),
                                "min_amount": float(cmin)
                            }
                        }
        return daily

    def save_daily_coupons(self):
        with open(self.daily_coupons_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for username, entry in self.daily_coupons.items():
                c = entry["coupon"]
                writer.writerow([username, entry["date"], c["code"], c["type"], c["value"], c["min_amount"]])

    # ------------------ USED COUPON STORAGE ------------------
    def load_used_coupons(self):
        used = {}
        if os.path.exists(self.used_coupons_file):
            with open(self.used_coupons_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        username, coupon_code = row
                        if username not in used:
                            used[username] = []
                        used[username].append(coupon_code)
        return used

    def save_used_coupons(self):
        with open(self.used_coupons_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for username, coupons in self.used_coupons.items():
                for coupon in coupons:
                    writer.writerow([username, coupon])

    # ------------------ AUTH & REGISTRATION ------------------
    def create_auth_interface(self):
        self.auth_frame = ttk.Frame(self.root)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor='center')

        auth_container = ttk.Frame(self.auth_frame)
        auth_container.pack(padx=40, pady=40)

        # Add a welcome message
        welcome_label = ttk.Label(auth_container, 
                                text="Welcome to Smart Cart!",
                                font=("Segoe UI", 20, "bold"))
        welcome_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        ttk.Label(auth_container, text="Username:", font=("Segoe UI", 12)).grid(row=1, column=0, pady=10, sticky='e', padx=10)
        self.username_entry = ttk.Entry(auth_container, width=35, font=("Segoe UI", 12))
        self.username_entry.grid(row=1, column=1, pady=10, padx=10)

        ttk.Label(auth_container, text="Password:", font=("Segoe UI", 12)).grid(row=2, column=0, pady=10, sticky='e', padx=10)
        self.password_entry = ttk.Entry(auth_container, show="•", width=35, font=("Segoe UI", 12))
        self.password_entry.grid(row=2, column=1, pady=10, padx=10)

        btn_frame = ttk.Frame(auth_container)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=30)
        ttk.Button(btn_frame, text="Sign In", command=self.authenticate, width=15).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="Register", command=self.create_register_interface, width=15).pack(side=tk.LEFT, padx=15)

    def create_register_interface(self):
        self.auth_frame.destroy()
        self.register_frame = ttk.Frame(self.root)
        self.register_frame.place(relx=0.5, rely=0.5, anchor='center')

        reg_container = ttk.Frame(self.register_frame)
        reg_container.pack(padx=40, pady=40)

        ttk.Label(reg_container, text="New Username:", font=("Segoe UI", 12)).grid(row=0, column=0, pady=15, sticky='e', padx=10)
        self.new_username_entry = ttk.Entry(reg_container, width=35, font=("Segoe UI", 12))
        self.new_username_entry.grid(row=0, column=1, pady=15, padx=10)

        ttk.Label(reg_container, text="New Password:", font=("Segoe UI", 12)).grid(row=1, column=0, pady=15, sticky='e', padx=10)
        self.new_password_entry = ttk.Entry(reg_container, show="•", width=35, font=("Segoe UI", 12))
        self.new_password_entry.grid(row=1, column=1, pady=15, padx=10)

        btn_frame = ttk.Frame(reg_container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=30)
        ttk.Button(btn_frame, text="Register", command=self.register_user, width=15).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="Back to Login", command=self.back_to_login, width=15).pack(side=tk.LEFT, padx=15)

    def is_strong_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        return True, "Password is strong"

    def register_user(self):
        new_user = self.new_username_entry.get().strip()
        new_pass = self.new_password_entry.get().strip()
        
        if not new_user or not new_pass:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return
            
        if new_user in self.users:
            messagebox.showerror("Error", "Username already exists")
            return
            
        # Check password strength
        is_strong, msg = self.is_strong_password(new_pass)
        if not is_strong:
            messagebox.showerror("Weak Password", msg)
            return
            
        self.users[new_user] = new_pass
        self.save_users()
        messagebox.showinfo("Success", "Registration successful! Please login")
        self.back_to_login()

    def back_to_login(self):
        self.register_frame.destroy()
        self.create_auth_interface()

    def authenticate(self):
        uname = self.username_entry.get()
        pwd = self.password_entry.get()
        if uname in self.users and self.users[uname] == pwd:
            self.logged_in_user = uname
            self.auth_frame.destroy()
            self.restore_daily_coupon_for_today()
            self.create_main_interface()
            self.update_display()
        else:
            messagebox.showerror("Authentication Failed", "Invalid credentials")

    # ------------------ DAILY COUPON RESTORE ------------------
    def restore_daily_coupon_for_today(self):
        today = str(datetime.date.today())
        user_coupon_entry = self.daily_coupons.get(self.logged_in_user)
        # Remove any previous day's daily coupon from base_coupons
        for code in list(self.base_coupons.keys()):
            if code not in ["WELCOME10", "FREESHIP", "BIGSPENDER"]:
                del self.base_coupons[code]
        # Restore today's coupon if exists
        if user_coupon_entry and user_coupon_entry["date"] == today:
            c = user_coupon_entry["coupon"]
            if c["code"] not in self.base_coupons:
                self.base_coupons[c["code"]] = {
                    "type": c["type"],
                    "value": c["value"],
                    "min_amount": c["min_amount"]
                }

    # ------------------ MAIN INTERFACE ------------------
    def create_main_interface(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Header with logout button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side=tk.LEFT)

        # Create a container for the main content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Products
        product_frame = ttk.LabelFrame(content_frame, text="Available Products")
        product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Create a canvas for products with scrollbar
        product_canvas = tk.Canvas(product_frame, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(product_frame, orient="vertical", command=product_canvas.yview)
        scrollable_frame = ttk.Frame(product_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: product_canvas.configure(scrollregion=product_canvas.bbox("all"))
        )

        product_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        product_canvas.configure(yscrollcommand=scrollbar.set)

        for idx, (prod, details) in enumerate(self.products.items()):
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Product info frame
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Product name and description
            ttk.Label(info_frame, 
                     text=prod,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ttk.Label(info_frame, 
                     text=details["description"],
                     font=("Segoe UI", 9)).pack(anchor="w")
            
            # Price and quantity frame
            price_qty_frame = ttk.Frame(item_frame)
            price_qty_frame.pack(side=tk.RIGHT, padx=10)
            
            ttk.Label(price_qty_frame, 
                     text=f"{self.currency_symbol}{details['price']:,.2f}",
                     font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=10)
            
            spinbox = ttk.Spinbox(price_qty_frame, from_=0, to=10, width=5,
                                command=lambda p=prod: self.update_quantity(p))
            spinbox.pack(side=tk.LEFT, padx=5)
            self.cart[prod] = {"var": tk.IntVar(value=0), "widget": spinbox}
            spinbox.config(textvariable=self.cart[prod]["var"])

        product_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side - Cart and Coupons
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Cart Summary
        summary_frame = ttk.LabelFrame(right_frame, text="Cart Summary")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        self.summary_text = tk.Text(summary_frame, height=12, width=50, 
                                  font=("Segoe UI", 10),
                                  background="#ffffff",
                                  relief="flat")
        self.summary_text.pack(padx=10, pady=10)

        # Checkout Button - Moved to a more visible position
        checkout_frame = ttk.Frame(right_frame)
        checkout_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(checkout_frame, 
                  text="Proceed to Checkout",
                  command=self.open_checkout_page,
                  width=20).pack(anchor=tk.CENTER, pady=5)

        # Coupons
        coupon_list_frame = ttk.LabelFrame(right_frame, text="Available Coupons")
        coupon_list_frame.pack(fill=tk.X, pady=(0, 10))
        self.coupon_list_text = tk.Text(coupon_list_frame, height=12, width=50,
                                      font=("Segoe UI", 10),
                                      background="#ffffff",
                                      relief="flat",
                                      state='disabled')
        self.coupon_list_text.pack(padx=10, pady=10)
        self.update_coupon_list()

        # Coupon Input
        coupon_frame = ttk.Frame(right_frame)
        coupon_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(coupon_frame, text="Apply Coupon:").pack(side=tk.LEFT, padx=5)
        self.coupon_input = ttk.Entry(coupon_frame, width=15)
        self.coupon_input.pack(side=tk.LEFT, padx=5)
        ttk.Button(coupon_frame, text="Apply", command=self.apply_coupon).pack(side=tk.LEFT, padx=5)
        self.remove_coupon_btn = ttk.Button(coupon_frame, text="Remove", 
                                          command=self.remove_coupon, state='disabled')
        self.remove_coupon_btn.pack(side=tk.LEFT, padx=5)

        # Lucky Draw
        self.lucky_frame = ttk.LabelFrame(right_frame, text="🎉 Daily Lucky Draw")
        self.lucky_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(self.lucky_frame, text="Get Lucky Coupon", 
                 command=self.get_lucky_coupon).pack(side=tk.LEFT, padx=10, pady=10)
        self.lucky_status = ttk.Label(self.lucky_frame, text="", font=("Segoe UI", 10))
        self.lucky_status.pack(side=tk.LEFT, padx=10, pady=10)

    def update_coupon_list(self):
        self.coupon_list_text.config(state='normal')
        self.coupon_list_text.delete(1.0, tk.END)
        
        # Configure text tags for styling
        self.coupon_list_text.tag_configure("header", font=("Segoe UI", 11, "bold"))
        self.coupon_list_text.tag_configure("coupon", font=("Segoe UI", 10))
        self.coupon_list_text.tag_configure("discount", font=("Segoe UI", 10), foreground="green")
        self.coupon_list_text.tag_configure("min_amount", font=("Segoe UI", 9), foreground="#666666")
        
        # Get user's used coupons
        user_used_coupons = self.used_coupons.get(self.logged_in_user, []) if self.logged_in_user else []
        
        default_coupons = [
            ("WELCOME10 - 10% off on any order", "WELCOME10"),
            ("FREESHIP - Free shipping (₹500 off)", "FREESHIP"),
            ("BIGSPENDER - 20% off on orders over ₹50,000", "BIGSPENDER")
        ]
        
        lucky_coupons = []
        for code in self.base_coupons:
            if code not in ["WELCOME10", "FREESHIP", "BIGSPENDER"]:
                coupon = self.base_coupons[code]
                if coupon["type"] == "percentage":
                    lucky_coupons.append((f"{code} - {int(coupon['value']*100)}% off", code))
                else:
                    lucky_coupons.append((f"{code} - ₹{coupon['value']} off", code))

        # Filter out used coupons for default coupons
        available_default_coupons = [c for c in default_coupons if c[1] not in user_used_coupons]
        # Filter out used coupons for lucky coupons
        available_lucky_coupons = [c for c in lucky_coupons if c[1] not in user_used_coupons]

        if available_default_coupons:
            self.coupon_list_text.insert(tk.END, "🎁 Default Coupons:\n", "header")
            for display_text, code in available_default_coupons:
                self.coupon_list_text.insert(tk.END, "• ", "coupon")
                if "FREESHIP" in code:
                    parts = display_text.split(" - ")
                    self.coupon_list_text.insert(tk.END, f"{parts[0]} - ", "coupon")
                    self.coupon_list_text.insert(tk.END, f"{parts[1]}\n", "discount")
                else:
                    parts = display_text.split(" - ")
                    self.coupon_list_text.insert(tk.END, f"{parts[0]} - ", "coupon")
                    self.coupon_list_text.insert(tk.END, f"{parts[1]}\n", "discount")

        if available_lucky_coupons:
            self.coupon_list_text.insert(tk.END, "\n🎲 Lucky Draw Coupons:\n", "header")
            for display_text, code in available_lucky_coupons:
                self.coupon_list_text.insert(tk.END, "• ", "coupon")
                parts = display_text.split(" - ")
                self.coupon_list_text.insert(tk.END, f"{parts[0]} - ", "coupon")
                self.coupon_list_text.insert(tk.END, f"{parts[1]}\n", "discount")
        
        if not available_default_coupons and not available_lucky_coupons:
            self.coupon_list_text.insert(tk.END, "😔 No coupons available at the moment.\n", "coupon")
        
        self.coupon_list_text.config(state='disabled')

    def get_lucky_coupon(self):
        if not self.logged_in_user:
            self.lucky_status.config(text="Please login first!", foreground='red')
            return
        today = str(datetime.date.today())
        user_coupon_entry = self.daily_coupons.get(self.logged_in_user)
        
        # If user has a coupon from a different day, remove it
        if user_coupon_entry and user_coupon_entry["date"] != today:
            old_code = user_coupon_entry["coupon"]["code"]
            if old_code in self.base_coupons:
                del self.base_coupons[old_code]
            del self.daily_coupons[self.logged_in_user]
            self.save_daily_coupons()
            user_coupon_entry = None
        
        if user_coupon_entry and user_coupon_entry["date"] == today:
            self.lucky_status.config(text="Come back tomorrow!", foreground='red')
            return

        prize_pool = [
            {"code": "MEGA30", "type": "percentage", "value": 0.30, "min_amount": 0},
            {"code": "FLASH25", "type": "percentage", "value": 0.25, "min_amount": 0},
            {"code": "SAVE5", "type": "percentage", "value": 0.05, "min_amount": 0},
            {"code": "TECH20", "type": "percentage", "value": 0.20, "min_amount": 0},
            {"code": "SHOP12", "type": "percentage", "value": 0.12, "min_amount": 0},
            {"code": "DEAL15", "type": "percentage", "value": 0.15, "min_amount": 0},
            {"code": "LUCKY18", "type": "percentage", "value": 0.18, "min_amount": 0},
            {"code": None, "type": None, "value": None, "min_amount": None}
        ]
        coupon = random.choice(prize_pool)
        if coupon["code"]:
            # Remove any previous day's daily coupon for this user from base_coupons
            for code in list(self.base_coupons.keys()):
                if code not in ["WELCOME10", "FREESHIP", "BIGSPENDER"]:
                    del self.base_coupons[code]
            self.base_coupons[coupon["code"]] = {
                "type": coupon["type"],
                "value": coupon["value"],
                "min_amount": coupon["min_amount"]
            }
            self.lucky_status.config(text=f"Won: {coupon['code']} coupon!", foreground='green')
            # Store in daily_coupons.csv
            self.daily_coupons[self.logged_in_user] = {
                "date": today,
                "coupon": {
                    "code": coupon["code"],
                    "type": coupon["type"],
                    "value": coupon["value"],
                    "min_amount": coupon["min_amount"]
                }
            }
            self.save_daily_coupons()
            self.update_coupon_list()
        else:
            self.lucky_status.config(text="Better luck next time!", foreground='red')
            # Still update the date so user can't spin again today
            self.daily_coupons[self.logged_in_user] = {
                "date": today,
                "coupon": {
                    "code": "",
                    "type": "",
                    "value": 0,
                    "min_amount": 0
                }
            }
            self.save_daily_coupons()

    def apply_coupon(self):
        code = self.coupon_input.get().strip().upper()
        if code in self.base_coupons:
            if self.applied_coupons:
                messagebox.showwarning("Notice", "Only one coupon can be applied at a time")
                return
            # Check if coupon is already used by the user
            if self.logged_in_user in self.used_coupons and code in self.used_coupons[self.logged_in_user]:
                messagebox.showerror("Error", "You have already used this coupon")
                return
            coupon = self.base_coupons[code]
            subtotal, _, _ = self.calculate_totals(ignore_coupon=True)
            if subtotal == 0:
                messagebox.showerror("Error", "Add items to cart before applying a coupon.")
                return
            if subtotal < coupon["min_amount"]:
                messagebox.showerror("Error", 
                    f"Minimum order amount of {self.currency_symbol}{coupon['min_amount']:,.2f} required")
                return
            discount_value = f"{int(coupon['value']*100)}%" if coupon["type"] == "percentage" else f"{self.currency_symbol}{coupon['value']}"
            messagebox.showinfo("Coupon Applied", f"✅ Applied {code}!\nDiscount: {discount_value}")
            self.applied_coupons = [code]
            self.remove_coupon_btn.config(state='normal')
        else:
            messagebox.showerror("Error", "Invalid coupon code")
        self.update_display()

    def remove_coupon(self):
        if self.applied_coupons:
            removed_code = self.applied_coupons.pop()
            messagebox.showinfo("Removed", f"Removed coupon: {removed_code}")
            self.remove_coupon_btn.config(state='disabled')
            self.update_display()

    def calculate_totals(self, ignore_coupon=False):
        subtotal = sum(self.products[p]["price"] * data["var"].get() for p, data in self.cart.items())
        discounts = 0
        shipping = 500 if subtotal > 0 else 0

        # Coupon eligibility check
        if not ignore_coupon and self.applied_coupons:
            code = self.applied_coupons[0]
            coupon = self.base_coupons.get(code)
            if not coupon:
                self.applied_coupons = []
                return subtotal, 0, subtotal + shipping
            if subtotal < coupon["min_amount"]:
                removed = self.applied_coupons.pop()
                messagebox.showwarning("Coupon Removed", 
                    f"{removed} coupon removed - order below minimum amount")
                self.remove_coupon_btn.config(state='disabled')
            else:
                if coupon["type"] == "percentage":
                    discounts += subtotal * coupon["value"]
                else:
                    if code == "FREESHIP":
                        discounts += shipping
                    else:
                        discounts += coupon["value"]

        total = max(subtotal - discounts + shipping - (500 if self.applied_coupons and self.applied_coupons[0] == "FREESHIP" else 0), 0)
        return subtotal, discounts, total

    def update_quantity(self, product):
        qty = self.cart[product]["var"].get()
        if qty < 0: 
            self.cart[product]["var"].set(0)
        self.update_display()

    def update_display(self):
        self.summary_text.delete(1.0, tk.END)
        subtotal, discounts, total = self.calculate_totals()
        shipping = 500 if subtotal > 0 else 0

        # Configure text tags for styling
        self.summary_text.tag_configure("header", font=("Segoe UI", 11, "bold"))
        self.summary_text.tag_configure("item", font=("Segoe UI", 10))
        self.summary_text.tag_configure("total_label", font=("Segoe UI", 11, "bold"))
        self.summary_text.tag_configure("total_value", font=("Segoe UI", 12, "bold"), foreground="#003366")
        self.summary_text.tag_configure("discount", font=("Segoe UI", 10), foreground="green")
        self.summary_text.tag_configure("shipping", font=("Segoe UI", 10))
        self.summary_text.tag_configure("coupon", font=("Segoe UI", 10), foreground="#0066cc")

        # Cart header
        self.summary_text.insert(tk.END, "🛒 Your Cart:\n", "header")
        
        # Cart items
        has_items = False
        for prod, data in self.cart.items():
            qty = data["var"].get()
            if qty > 0:
                has_items = True
                item_price = self.products[prod]['price'] * qty
                self.summary_text.insert(tk.END, f"• {prod}\n", "item")
                self.summary_text.insert(tk.END, f"  Quantity: {qty} × {self.currency_symbol}{self.products[prod]['price']:,.2f} = {self.currency_symbol}{item_price:,.2f}\n", "item")
        
        if not has_items:
            self.summary_text.insert(tk.END, "Your cart is empty\n", "item")
        
        # Totals section
        self.summary_text.insert(tk.END, "\n💵 Order Summary:\n", "header")
        
        # Subtotal
        self.summary_text.insert(tk.END, "Subtotal: ", "total_label")
        self.summary_text.insert(tk.END, f"{self.currency_symbol}{subtotal:,.2f}\n", "item")
        
        # Shipping
        shipping_cost = shipping - (500 if self.applied_coupons and self.applied_coupons[0] == "FREESHIP" else 0)
        self.summary_text.insert(tk.END, "Shipping: ", "total_label")
        if shipping_cost == 0:
            self.summary_text.insert(tk.END, "FREE\n", "discount")
        else:
            self.summary_text.insert(tk.END, f"{self.currency_symbol}{shipping_cost:,.2f}\n", "shipping")
        
        # Discounts
        if discounts > 0:
            self.summary_text.insert(tk.END, "Discounts: ", "total_label")
            self.summary_text.insert(tk.END, f"-{self.currency_symbol}{discounts:,.2f}\n", "discount")
        
        # Total
        self.summary_text.insert(tk.END, "\nTotal: ", "total_label")
        self.summary_text.insert(tk.END, f"{self.currency_symbol}{total:,.2f}\n", "total_value")
        
        # Applied coupon
        if self.applied_coupons:
            self.summary_text.insert(tk.END, "\n🎫 Applied Coupon:\n", "header")
            self.summary_text.insert(tk.END, f"• {self.applied_coupons[0]}\n", "coupon")

    def open_checkout_page(self):
        if not any(data["var"].get() > 0 for data in self.cart.values()):
            messagebox.showerror("Empty Cart", "Please add items to your cart first!")
            return

        checkout_win = tk.Toplevel(self.root)
        checkout_win.title("Checkout")
        checkout_win.geometry("600x800")
        checkout_win.configure(bg="#f0f0f0")

        checkout_win.transient(self.root)
        checkout_win.grab_set()

        def validate_numeric(P):
            return P.isdigit() or P == ""

        def validate_name(P):
            return all(c.isalpha() or c.isspace() for c in P)

        def validate_postal_code(P):
            return len(P) <= 6 and (P.isdigit() or P == "")

        def validate_card_number(P):
            return len(P) <= 16 and (P.isdigit() or P == "")

        def validate_cvv(P):
            return len(P) <= 3 and (P.isdigit() or P == "")

        def validate_expiry(P):
            if P == "":
                return True
            
            if not all(c.isdigit() or c == '/' for c in P):
                return False
            
            if len(P) > 5:
                return False
                
            return True

        def format_expiry(event):
            entry = event.widget
            current = entry.get()
            
            if not current or '/' in current:
                return
            
            if len(current) == 2 and current.isdigit():
                entry.insert(2, '/')

        def validate_upi(P):
            if P == "":
                return True
            if ' ' in P:
                return False
            if '@' not in P:
                return P.isalnum()
            parts = P.split('@')
            if len(parts) != 2:
                return False
            username, domain = parts
            if not username or not username.isalnum():
                return False
            if domain and not 'bank'.startswith(domain.lower()):
                return False
            return True

        vcmd_numeric = (checkout_win.register(validate_numeric), '%P')
        vcmd_name = (checkout_win.register(validate_name), '%P')
        vcmd_postal = (checkout_win.register(validate_postal_code), '%P')
        vcmd_card = (checkout_win.register(validate_card_number), '%P')
        vcmd_cvv = (checkout_win.register(validate_cvv), '%P')
        vcmd_expiry = (checkout_win.register(validate_expiry), '%P')
        vcmd_upi = (checkout_win.register(validate_upi), '%P')

        # Create main scrollable frame
        main_canvas = tk.Canvas(checkout_win, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(checkout_win, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header_frame, 
                 text="Checkout",
                 font=("Segoe UI", 16, "bold")).pack()

        # Order Summary
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Order Summary")
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        subtotal, discounts, total = self.calculate_totals()
        shipping = 500 if subtotal > 0 else 0
        
        summary_text = tk.Text(summary_frame, height=6, width=50,
                             font=("Segoe UI", 10),
                             background="#ffffff",
                             relief="flat")
        summary_text.pack(padx=10, pady=10)
        
        summary_text.insert(tk.END, f"Subtotal: {self.currency_symbol}{subtotal:,.2f}\n")
        summary_text.insert(tk.END, f"Shipping: {self.currency_symbol}{shipping:,.2f}\n")
        summary_text.insert(tk.END, f"Discounts: -{self.currency_symbol}{discounts:,.2f}\n")
        summary_text.insert(tk.END, f"Total: {self.currency_symbol}{total:,.2f}\n")
        summary_text.config(state='disabled')

        # Billing Information
        billing_frame = ttk.LabelFrame(scrollable_frame, text="Billing Information")
        billing_frame.pack(fill=tk.X, padx=20, pady=10)

        fields = [
            ("Full Name*", True, vcmd_name),
            ("Address Line 1*", True, None),
            ("Address Line 2", False, None),
            ("City*", True, vcmd_name),
            ("State*", True, vcmd_name),
            ("Postal Code*", True, vcmd_postal),
            ("Country*", True, vcmd_name)
        ]

        entries = {}
        for idx, (label_text, required, validation) in enumerate(fields):
            field_frame = ttk.Frame(billing_frame)
            field_frame.pack(fill=tk.X, pady=5, padx=10)
            
            label = ttk.Label(field_frame, text=label_text)
            label.pack(side=tk.LEFT, anchor='w')
            
            entry = ttk.Entry(field_frame, width=35, validate='key')
            if validation:
                entry.config(validatecommand=validation)
            entry.pack(side=tk.RIGHT, padx=5)
            entries[label_text.strip("*:")] = (entry, required)

        # Payment Information
        payment_frame = ttk.LabelFrame(scrollable_frame, text="Payment Information")
        payment_frame.pack(fill=tk.X, padx=20, pady=10)

        # Payment Method
        payment_method_frame = ttk.Frame(payment_frame)
        payment_method_frame.pack(fill=tk.X, pady=5, padx=10)
        ttk.Label(payment_method_frame, text="Payment Method*").pack(side=tk.LEFT)
        payment_method = tk.StringVar(value="credit_card")
        ttk.Radiobutton(payment_method_frame, text="Credit Card", 
                       variable=payment_method, value="credit_card").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(payment_method_frame, text="Debit Card", 
                       variable=payment_method, value="debit_card").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(payment_method_frame, text="UPI", 
                       variable=payment_method, value="upi").pack(side=tk.LEFT, padx=20)

        # Card Details (shown by default)
        card_frame = ttk.Frame(payment_frame)
        card_frame.pack(fill=tk.X, pady=5, padx=10)
        
        card_fields = [
            ("Card Number*", True, vcmd_card),
            ("Card Holder Name*", True, vcmd_name),
            ("Expiry Date (MM/YY)*", True, vcmd_expiry),
            ("CVV*", True, vcmd_cvv)
        ]

        card_entries = {}
        for idx, (label_text, required, validation) in enumerate(card_fields):
            field_frame = ttk.Frame(card_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(field_frame, text=label_text)
            label.pack(side=tk.LEFT, anchor='w')
            
            entry = ttk.Entry(field_frame, width=35, validate='key')
            if validation:
                entry.config(validatecommand=validation)
            if "Expiry" in label_text:
                # Add automatic slash after month input
                entry.bind('<KeyRelease>', format_expiry)
            entry.pack(side=tk.RIGHT, padx=5)
            card_entries[label_text.strip("*:")] = (entry, required)

        # UPI ID (hidden by default)
        upi_frame = ttk.Frame(payment_frame)
        ttk.Label(upi_frame, text="UPI ID*").pack(side=tk.LEFT, anchor='w')
        upi_entry = ttk.Entry(upi_frame, width=35, validate='key', validatecommand=vcmd_upi)
        upi_entry.pack(side=tk.RIGHT, padx=5)

        def toggle_payment_fields():
            if payment_method.get() == "upi":
                card_frame.pack_forget()
                upi_frame.pack(fill=tk.X, pady=5, padx=10)
            else:
                upi_frame.pack_forget()
                card_frame.pack(fill=tk.X, pady=5, padx=10)

        # Bind payment method change
        payment_method.trace_add("write", lambda *args: toggle_payment_fields())

        # Place Order button
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def submit_order():
            errors = []
            # Validate billing information
            for field, (entry, required) in entries.items():
                value = entry.get().strip()
                if required and not value:
                    errors.append(f"{field} is required")
                if field == "Postal Code" and value and not value.isdigit():
                    errors.append("Postal Code must be numeric")
                if field == "Full Name" and value and not all(c.isalpha() or c.isspace() for c in value):
                    errors.append("Full Name must contain only letters and spaces")
            
            # Validate payment information
            if payment_method.get() in ["credit_card", "debit_card"]:
                for field, (entry, required) in card_entries.items():
                    value = entry.get().strip()
                    if required and not value:
                        errors.append(f"{field} is required")
                    if field == "Card Number" and value and (not value.isdigit() or len(value) != 16):
                        errors.append("Card Number must be 16 digits")
                    if field == "CVV" and value and (not value.isdigit() or len(value) != 3):
                        errors.append("CVV must be 3 digits")
                    if field == "Expiry Date" and value:
                        # Validate expiry date format and value
                        if '/' not in value or len(value) != 5:
                            errors.append("Expiry Date must be in MM/YY format")
                        else:
                            try:
                                month, year = value.split('/')
                                month_num = int(month)
                                year_num = int(year)
                                
                                # Check month range
                                if not (1 <= month_num <= 12):
                                    errors.append("Month must be between 01 and 12")
                                    
                                # Get current date
                                current_year = datetime.datetime.now().year % 100
                                current_month = datetime.datetime.now().month
                                
                                # Check if card is expired
                                if year_num < current_year or (year_num == current_year and month_num < current_month):
                                    errors.append("Card has expired")
                                    
                                # Check if year is too far in the future (optional)
                                if year_num > current_year + 10:
                                    errors.append("Invalid expiry year")
                            except ValueError:
                                errors.append("Invalid expiry date format")
            else:
                upi_value = upi_entry.get().strip()
                if not upi_value:
                    errors.append("UPI ID is required")
                elif not upi_value.endswith('@bank'):
                    errors.append("Invalid UPI ID format. Must be in format: username@bank")
                elif not upi_value.split('@')[0].isalnum():
                    errors.append("UPI username must contain only letters and numbers")
                elif len(upi_value.split('@')[0]) < 3:
                    errors.append("UPI username must be at least 3 characters long")

            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            # Mark the applied coupon as used if there is one
            if self.applied_coupons:
                self.mark_coupon_as_used(self.logged_in_user, self.applied_coupons[0])
                # Update the coupon list immediately after marking as used
                self.update_coupon_list()
            
            messagebox.showinfo("Order Placed", "Thank you for your purchase!")
            checkout_win.destroy()
            self.reset_cart()

        ttk.Button(button_frame, 
                  text="Place Order",
                  command=submit_order).pack(side=tk.RIGHT)

        # Pack the canvas and scrollbar
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def logout(self):
        self.logged_in_user = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_auth_interface()

    def reset_cart(self):
        for data in self.cart.values():
            data["var"].set(0)
        self.applied_coupons = []
        self.coupon_input.delete(0, tk.END)
        self.remove_coupon_btn.config(state='disabled')
        self.update_display()

    def mark_coupon_as_used(self, username, coupon_code):
        if username not in self.used_coupons:
            self.used_coupons[username] = []
        if coupon_code not in self.used_coupons[username]:
            self.used_coupons[username].append(coupon_code)
            self.save_used_coupons()
            # Remove the coupon from base_coupons if it's a daily coupon
            if coupon_code in self.base_coupons and coupon_code not in ["WELCOME10", "FREESHIP", "BIGSPENDER"]:
                del self.base_coupons[coupon_code]

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedShoppingCart(root)
    root.mainloop()
