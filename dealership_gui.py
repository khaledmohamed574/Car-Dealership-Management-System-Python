import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import date

# ==============================================================================
# 0. DATABASE INTEGRATION FOR LOCAL PERSISTENCE (SQLite)
# ==============================================================================

class DealershipDatabase:
    def __init__(self, db_path="dealership.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    car_id TEXT PRIMARY KEY,
                    brand TEXT,
                    model TEXT,
                    year INTEGER,
                    category TEXT,
                    mileage INTEGER,
                    condition TEXT,
                    status TEXT,
                    purchase_price REAL,
                    selling_price REAL,
                    warranty_period INTEGER,
                    previous_owners INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT,
                    phone TEXT,
                    email TEXT,
                    register_date TEXT,
                    loyalty_points INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    name TEXT,
                    role TEXT,
                    salary REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id TEXT PRIMARY KEY,
                    sale_date TEXT,
                    car_id TEXT,
                    customer_id TEXT,
                    employee_id TEXT,
                    final_price REAL,
                    discount REAL,
                    tax REAL,
                    profit REAL,
                    status TEXT,
                    FOREIGN KEY(car_id) REFERENCES cars(car_id),
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
                )
            """)
            
            # Seed default employees if empty
            cursor.execute("SELECT COUNT(*) FROM employees")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO employees (employee_id, name, role, salary)
                    VALUES (?, ?, ?, ?)
                """, [
                    ("EMP-100", "Sarah Jenkins", "Manager", 95000.0),
                    ("EMP-101", "Marcus Vance", "Sales Agent", 50000.0)
                ])
                
            # Seed default customers if empty
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO customers (customer_id, name, phone, email, register_date, loyalty_points)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    ("CUST-001", "Bruce Wayne", "+1-555-7777", "bruce@waynecorp.com", date.today().isoformat(), 1200),
                    ("CUST-002", "Clark Kent", "+1-555-8888", "clark@dailyplanet.com", date.today().isoformat(), 350)
                ])

            # Seed default cars if empty
            cursor.execute("SELECT COUNT(*) FROM cars")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO cars (car_id, brand, model, year, category, mileage, condition, status, purchase_price, selling_price, warranty_period, previous_owners)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    ("CAR-001", "Porsche", "911 Carrera S", 2022, "Sports", 12500, "Used", "Available", 110000.0, 124900.0, 0, 1),
                    ("CAR-002", "Tesla", "Model Y", 2024, "SUV", 0, "New", "Available", 42000.0, 48990.0, 48, 0),
                    ("CAR-003", "Mercedes-Benz", "G-Class", 2021, "SUV", 24000, "Used", "Available", 145000.0, 168000.0, 0, 1)
                ])
            conn.commit()


# ==============================================================================
# 1. CORE OBJECT-ORIENTED PROGRAMMING (OOP) MODELS
# ==============================================================================

class Car:
    def __init__(self, car_id, brand, model, year, category, mileage, condition, purchase_price, selling_price):
        self.carID = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.category = category
        self.mileage = mileage
        self.condition = condition  # "New" or "Used"
        self.status = "Available"   # "Available", "Sold", "UnderMaintenance"
        self.purchasePrice = float(purchase_price)
        self.sellingPrice = float(selling_price)

    def calculate_profit(self):
        return self.sellingPrice - self.purchasePrice

    def __str__(self):
        return f"{self.year} {self.brand} {self.model} ({self.condition})"


class NewCar(Car):
    def __init__(self, car_id, brand, model, year, category, purchase_price, selling_price, warranty_period=48):
        super().__init__(car_id, brand, model, year, category, 0, "New", purchase_price, selling_price)
        self.warrantyPeriod = warranty_period  # In months


class UsedCar(Car):
    def __init__(self, car_id, brand, model, year, category, mileage, purchase_price, selling_price, previous_owners=1):
        super().__init__(car_id, brand, model, year, category, mileage, "Used", purchase_price, selling_price)
        self.previousOwners = previous_owners


class Customer:
    def __init__(self, customer_id, name, phone, email, register_date=None, loyalty_points=0):
        self.customerID = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.registerDate = register_date or date.today().isoformat()
        self.loyaltyPoints = loyalty_points
        self.purchase_history = []


class Employee:
    def __init__(self, employee_id, name, role, salary):
        self.employeeID = employee_id
        self.name = name
        self.role = role
        self.salary = salary


class Sale:
    def __init__(self, sale_id, car, customer, employee, final_price, discount=0.0):
        self.saleID = sale_id
        self.date = date.today().isoformat()
        self.car = car
        self.customer = customer
        self.employee = employee
        self.finalPrice = float(final_price)
        self.discount = float(discount)
        self.tax = self.finalPrice * 0.08
        self.profit = self.finalPrice - car.purchasePrice
        self.status = "Completed"


class CarDealership:
    def __init__(self, name, db_path="dealership.db"):
        self.name = name
        self.db = DealershipDatabase(db_path)

    def get_cars(self):
        cars = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars")
            rows = cursor.fetchall()
            for r in rows:
                if r[6] == "New":
                    car = NewCar(r[0], r[1], r[2], r[3], r[4], r[8], r[9], r[10])
                else:
                    car = UsedCar(r[0], r[1], r[2], r[3], r[4], r[5], r[8], r[9], r[11])
                car.status = r[7]
                cars.append(car)
        return cars

    def get_customers(self):
        customers = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, COUNT(s.sale_id) 
                FROM customers c 
                LEFT JOIN sales s ON c.customer_id = s.customer_id 
                GROUP BY c.customer_id
            """)
            rows = cursor.fetchall()
            for r in rows:
                cust = Customer(r[0], r[1], r[2], r[3], r[4], r[5])
                cust.purchase_count = r[6]
                customers.append(cust)
        return customers

    def get_employees(self):
        employees = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees")
            rows = cursor.fetchall()
            for r in rows:
                employees.append(Employee(r[0], r[1], r[2], r[3]))
        return employees

    def add_car(self, car):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            warranty = getattr(car, "warrantyPeriod", 0)
            prev_owners = getattr(car, "previousOwners", 0)
            cursor.execute("""
                INSERT INTO cars (car_id, brand, model, year, category, mileage, condition, status, purchase_price, selling_price, warranty_period, previous_owners)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (car.carID, car.brand, car.model, car.year, car.category, car.mileage, car.condition, car.status, car.purchasePrice, car.sellingPrice, warranty, prev_owners))
            conn.commit()

    def register_customer(self, customer):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (customer_id, name, phone, email, register_date, loyalty_points)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer.customerID, customer.name, customer.phone, customer.email, customer.registerDate, customer.loyaltyPoints))
            conn.commit()

    def record_sale(self, sale):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Save sale
            cursor.execute("""
                INSERT INTO sales (sale_id, sale_date, car_id, customer_id, employee_id, final_price, discount, tax, profit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sale.saleID, sale.date, sale.car.carID, sale.customer.customerID, sale.employee.employeeID, sale.finalPrice, sale.discount, sale.tax, sale.profit, sale.status))
            # 2. Update car status
            cursor.execute("UPDATE cars SET status = 'Sold' WHERE car_id = ?", (sale.car.carID,))
            # 3. Update customer loyalty points
            earned_points = int(sale.finalPrice / 100)
            cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + ? WHERE customer_id = ?", (earned_points, sale.customer.customerID))
            conn.commit()

    def calculate_total_profit(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(profit) FROM sales WHERE status = 'Completed'")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0.0

    def calculate_total_revenue(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(final_price) FROM sales WHERE status = 'Completed'")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0.0


# ==============================================================================
# 2. DESKTOP GUI IMPLEMENTATION USING TKINTER & TTK
# ==============================================================================

class DealershipGUI(tk.Tk):
    def __init__(self, dealership):
        super().__init__()
        self.dealership = dealership
        self.title(f"{dealership.name} - Admin Portal (Python OOP & SQLite)")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Style Configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Configure Colors
        self.style.configure(".", background="#f8fafc", foreground="#1e293b", font=("Segoe UI", 10))
        self.style.configure("TLabel", background="#f8fafc", foreground="#1e293b")
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#4f46e5")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"), foreground="#0f172a")
        
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background="#4f46e5", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[("active", "#4338ca")])
        self.style.configure("Secondary.TButton", background="#64748b", foreground="white")
        self.style.map("Secondary.TButton", background=[("active", "#475569")])
        
        self.style.configure("TFrame", background="#f8fafc")
        self.style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid")
        self.style.configure("TNotebook", background="#f1f5f9", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])
        
        # Setup Layout
        self.setup_ui()

    def setup_ui(self):
        # Header banner
        header_frame = ttk.Frame(self, padding=15)
        header_frame.pack(fill="x", side="top")
        
        title_lbl = ttk.Label(header_frame, text=f"✨ {self.dealership.name}", style="Header.TLabel")
        title_lbl.pack(side="left")
        
        subtitle_lbl = ttk.Label(header_frame, text="Desktop Management & CRM Studio", font=("Segoe UI", 10, "italic"), foreground="#64748b")
        subtitle_lbl.pack(side="left", padx=15, pady=8)

        # Main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Register Tabs
        self.tab_dashboard = ttk.Frame(self.notebook, padding=15)
        self.tab_inventory = ttk.Frame(self.notebook, padding=15)
        self.tab_customers = ttk.Frame(self.notebook, padding=15)
        self.tab_sales = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_inventory, text="Showroom Inventory")
        self.notebook.add(self.tab_customers, text="Customers & CRM")
        self.notebook.add(self.tab_sales, text="New Sales Transaction")

        # Build each screen
        self.build_dashboard()
        self.build_inventory()
        self.build_customers()
        self.build_sales()
        
        # Initial Refresh
        self.refresh_dashboard()

    # --------------------------------------------------------------------------
    # DASHBOARD TAB
    # --------------------------------------------------------------------------
    def build_dashboard(self):
        lbl = ttk.Label(self.tab_dashboard, text="Real-Time OOP Business Metrics", style="Subheader.TLabel")
        lbl.pack(anchor="w", pady=(0, 15))

        # KPI Cards container
        kpi_container = ttk.Frame(self.tab_dashboard)
        kpi_container.pack(fill="x", pady=10)

        # KPI 1: Revenue
        card_rev = ttk.Frame(kpi_container, padding=15, style="Card.TFrame")
        card_rev.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(card_rev, text="TOTAL SALES REVENUE", font=("Segoe UI", 9, "bold"), foreground="#64748b").pack(anchor="w")
        self.lbl_rev_val = ttk.Label(card_rev, text="\$0.00", font=("Segoe UI", 18, "bold"), foreground="#10b981")
        self.lbl_rev_val.pack(anchor="w", pady=5)

        # KPI 2: Profit
        card_prof = ttk.Frame(kpi_container, padding=15, style="Card.TFrame")
        card_prof.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(card_prof, text="GROSS OOP PROFIT", font=("Segoe UI", 9, "bold"), foreground="#64748b").pack(anchor="w")
        self.lbl_prof_val = ttk.Label(card_prof, text="\$0.00", font=("Segoe UI", 18, "bold"), foreground="#4f46e5")
        self.lbl_prof_val.pack(anchor="w", pady=5)

        # KPI 3: Available Cars
        card_cars = ttk.Frame(kpi_container, padding=15, style="Card.TFrame")
        card_cars.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(card_cars, text="AVAILABLE VEHICLES", font=("Segoe UI", 9, "bold"), foreground="#64748b").pack(anchor="w")
        self.lbl_cars_val = ttk.Label(card_cars, text="0", font=("Segoe UI", 18, "bold"), foreground="#f59e0b")
        self.lbl_cars_val.pack(anchor="w", pady=5)

        # Quick Logs Console in Dashboard
        console_frame = ttk.LabelFrame(self.tab_dashboard, text=" Dealership Audit Logging Terminal ", padding=10)
        console_frame.pack(fill="both", expand=True, pady=15)

        self.console_text = tk.Text(console_frame, height=10, bg="#0f172a", fg="#38bdf8", font=("Consolas", 10), borderwidth=0)
        self.console_text.pack(fill="both", expand=True)
        self.log_message("System launched. OOP Database connection established (Local SQLite - dealership.db).")

    def log_message(self, text):
        self.console_text.insert(tk.END, f"[{date.today().isoformat()}] {text}\n")
        self.console_text.see(tk.END)

    def refresh_dashboard(self):
        revenue = self.dealership.calculate_total_revenue()
        profit = self.dealership.calculate_total_profit()
        available = len([c for c in self.dealership.get_cars() if c.status == "Available"])
        
        self.lbl_rev_val.config(text=f"\${revenue:,.2f}")
        self.lbl_prof_val.config(text=f"\${profit:,.2f}")
        self.lbl_cars_val.config(text=str(available))

    # --------------------------------------------------------------------------
    # INVENTORY SHOWROOM TAB
    # --------------------------------------------------------------------------
    def build_inventory(self):
        # Two pane layout: Left is Table, Right is Registration
        paned = ttk.PanedWindow(self.tab_inventory, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_pane = ttk.Frame(paned, padding=5)
        right_pane = ttk.Frame(paned, padding=10, style="Card.TFrame")
        paned.add(left_pane, weight=3)
        paned.add(right_pane, weight=1)

        # Left: Search & Table
        search_frame = ttk.Frame(left_pane)
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_frame, text="Search Stock: ").pack(side="left")
        self.ent_car_search = ttk.Entry(search_frame, width=25)
        self.ent_car_search.pack(side="left", padx=5)
        self.ent_car_search.bind("<KeyRelease>", self.filter_cars)

        # Table (Treeview)
        cols = ("ID", "Brand", "Model", "Year", "Condition", "Mileage", "Price", "Status")
        self.car_tree = ttk.Treeview(left_pane, columns=cols, show="headings", height=15)
        for col in cols:
            self.car_tree.heading(col, text=col)
            self.car_tree.column(col, width=80 if col in ["ID", "Year", "Condition"] else 110, anchor="center")
        
        scrollbar = ttk.Scrollbar(left_pane, orient="vertical", command=self.car_tree.yview)
        self.car_tree.configure(yscrollcommand=scrollbar.set)
        
        self.car_tree.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")

        # Right Pane: Add Vehicle Form
        ttk.Label(right_pane, text="Register New Vehicle", font=("Segoe UI", 11, "bold"), foreground="#4f46e5").grid(row=0, column=0, columnspan=2, pady=(0,15))
        
        labels = ["Brand:", "Model:", "Year:", "Category:", "Mileage:", "Purchase Price (\$):", "Selling Price (\$):", "Condition:"]
        self.car_entries = {}
        
        for idx, lbl_text in enumerate(labels):
            ttk.Label(right_pane, text=lbl_text).grid(row=idx+1, column=0, sticky="w", pady=5)
            if lbl_text == "Condition:":
                self.car_entries[lbl_text] = ttk.Combobox(right_pane, values=["New", "Used"], state="readonly", width=18)
                self.car_entries[lbl_text].set("New")
            else:
                self.car_entries[lbl_text] = ttk.Entry(right_pane, width=20)
            self.car_entries[lbl_text].grid(row=idx+1, column=1, pady=5, padx=5)

        btn_add = ttk.Button(right_pane, text="Save Vehicle Object", command=self.add_car_action)
        btn_add.grid(row=len(labels)+1, column=0, columnspan=2, pady=20, sticky="ew")

        self.populate_car_table()

    def populate_car_table(self, filter_text=""):
        self.car_tree.delete(*self.car_tree.get_children())
        for car in self.dealership.get_cars():
            if filter_text.lower() in f"{car.brand} {car.model}".lower():
                self.car_tree.insert("", "end", values=(
                    car.carID, car.brand, car.model, car.year, car.condition, 
                    f"{car.mileage:,} mi", f"\${car.sellingPrice:,.2f}", car.status
                ))

    def filter_cars(self, event=None):
        txt = self.ent_car_search.get()
        self.populate_car_table(txt)

    def add_car_action(self):
        try:
            brand = self.car_entries["Brand:"].get().strip()
            model = self.car_entries["Model:"].get().strip()
            year = int(self.car_entries["Year:"].get())
            category = self.car_entries["Category:"].get().strip()
            mileage = int(self.car_entries["Mileage:"].get() or 0)
            p_price = float(self.car_entries["Purchase Price (\$):"].get())
            s_price = float(self.car_entries["Selling Price (\$):"].get())
            cond = self.car_entries["Condition:"].get()

            if not brand or not model:
                raise ValueError("Brand and Model are required.")

            car_id = f"CAR-{str(uuid.uuid4())[:4].upper()}"
            if cond == "New":
                car = NewCar(car_id, brand, model, year, category, p_price, s_price)
            else:
                car = UsedCar(car_id, brand, model, year, category, mileage, p_price, s_price)

            self.dealership.add_car(car)
            self.log_message(f"Instantiated subclass {cond}Car: {car_id} ({brand} {model}) saved to SQLite database.")
            
            # Clear entries
            for key in self.car_entries:
                if isinstance(self.car_entries[key], ttk.Entry):
                    self.car_entries[key].delete(0, tk.END)
            
            self.populate_car_table()
            self.refresh_dashboard()
            self.refresh_sales_selectors()
            messagebox.showinfo("Success", f"Vehicle object {car_id} created and stored in database successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input values: {str(e)}")

    # --------------------------------------------------------------------------
    # CUSTOMERS TAB
    # --------------------------------------------------------------------------
    def build_customers(self):
        paned = ttk.PanedWindow(self.tab_customers, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_pane = ttk.Frame(paned, padding=5)
        right_pane = ttk.Frame(paned, padding=10, style="Card.TFrame")
        paned.add(left_pane, weight=3)
        paned.add(right_pane, weight=1)

        # Table (Treeview)
        cols = ("Customer ID", "Name", "Phone", "Email", "Loyalty Points", "Active Purchases")
        self.cust_tree = ttk.Treeview(left_pane, columns=cols, show="headings", height=15)
        for col in cols:
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, width=120, anchor="center")

        scrollbar = ttk.Scrollbar(left_pane, orient="vertical", command=self.cust_tree.yview)
        self.cust_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cust_tree.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")

        # Right: Add Customer
        ttk.Label(right_pane, text="Register New Customer", font=("Segoe UI", 11, "bold"), foreground="#4f46e5").grid(row=0, column=0, columnspan=2, pady=(0,15))
        
        labels = ["Name:", "Phone:", "Email:", "Loyalty Points:"]
        self.cust_entries = {}
        
        for idx, lbl_text in enumerate(labels):
            ttk.Label(right_pane, text=lbl_text).grid(row=idx+1, column=0, sticky="w", pady=5)
            self.cust_entries[lbl_text] = ttk.Entry(right_pane, width=20)
            self.cust_entries[lbl_text].grid(row=idx+1, column=1, pady=5, padx=5)
            if lbl_text == "Loyalty Points:":
                self.cust_entries[lbl_text].insert(0, "0")

        btn_add = ttk.Button(right_pane, text="Save Customer Object", command=self.add_customer_action)
        btn_add.grid(row=len(labels)+1, column=0, columnspan=2, pady=20, sticky="ew")

        self.populate_customer_table()

    def populate_customer_table(self):
        self.cust_tree.delete(*self.cust_tree.get_children())
        for cust in self.dealership.get_customers():
            self.cust_tree.insert("", "end", values=(
                cust.customerID, cust.name, cust.phone, cust.email, cust.loyaltyPoints, getattr(cust, "purchase_count", 0)
            ))

    def add_customer_action(self):
        try:
            name = self.cust_entries["Name:"].get().strip()
            phone = self.cust_entries["Phone:"].get().strip()
            email = self.cust_entries["Email:"].get().strip()
            points = int(self.cust_entries["Loyalty Points:"].get() or 0)

            if not name:
                raise ValueError("Customer Name is required.")

            cust_id = f"CUST-{str(uuid.uuid4())[:4].upper()}"
            customer = Customer(cust_id, name, phone, email, loyalty_points=points)
            self.dealership.register_customer(customer)
            self.log_message(f"Instantiated Customer Object: {cust_id} ({name}) saved to database.")

            # Clear inputs
            for key in self.cust_entries:
                self.cust_entries[key].delete(0, tk.END)
                if key == "Loyalty Points:":
                    self.cust_entries[key].insert(0, "0")

            self.populate_customer_table()
            self.refresh_sales_selectors()
            messagebox.showinfo("Success", f"Customer {cust_id} registered successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid customer details: {str(e)}")

    # --------------------------------------------------------------------------
    # TRANSACTION SALES TAB
    # --------------------------------------------------------------------------
    def build_sales(self):
        # Interactive Sales form to link Customer & Vehicle & Salesperson objects
        ttk.Label(self.tab_sales, text="Execute New Sales Pipeline Transaction", style="Subheader.TLabel").pack(anchor="w", pady=(0, 15))

        form_frame = ttk.Frame(self.tab_sales, padding=20, style="Card.TFrame")
        form_frame.pack(fill="x", pady=10)

        # Fields
        ttk.Label(form_frame, text="Select Customer Profile:").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.cb_sales_cust = ttk.Combobox(form_frame, state="readonly", width=40)
        self.cb_sales_cust.grid(row=0, column=1, pady=10, padx=10)

        # Vehicle field (will look up available vehicles from DB)
        ttk.Label(form_frame, text="Select Available Car Object:").grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.cb_sales_car = ttk.Combobox(form_frame, state="readonly", width=40)
        self.cb_sales_car.grid(row=1, column=1, pady=10, padx=10)

        ttk.Label(form_frame, text="Responsible Sales Agent:").grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.cb_sales_emp = ttk.Combobox(form_frame, state="readonly", width=40)
        self.cb_sales_emp.grid(row=2, column=1, pady=10, padx=10)

        ttk.Label(form_frame, text="Final Negotiated Price (\$):").grid(row=3, column=0, sticky="w", pady=10, padx=10)
        self.ent_sales_price = ttk.Entry(form_frame, width=42)
        self.ent_sales_price.grid(row=3, column=1, pady=10, padx=10)

        ttk.Label(form_frame, text="Applied Discount (\$):").grid(row=4, column=0, sticky="w", pady=10, padx=10)
        self.ent_sales_disc = ttk.Entry(form_frame, width=42)
        self.ent_sales_disc.grid(row=4, column=1, pady=10, padx=10)
        self.ent_sales_disc.insert(0, "0.0")

        btn_execute = ttk.Button(form_frame, text="Process Transaction & Print Invoice", command=self.process_sale_action, padding=8)
        btn_execute.grid(row=5, column=0, columnspan=2, pady=25, sticky="ew")

        self.refresh_sales_selectors()

    def refresh_sales_selectors(self):
        # Customers dropdown list
        cust_list = [f"{c.customerID} - {c.name}" for c in self.dealership.get_customers()]
        self.cb_sales_cust["values"] = cust_list
        if cust_list:
            self.cb_sales_cust.current(0)

        # Available vehicles dropdown list
        car_list = [f"{c.carID} - {c.brand} {c.model} (\${c.sellingPrice:,.2f})" for c in self.dealership.get_cars() if c.status == "Available"]
        self.cb_sales_car["values"] = car_list
        if car_list:
            self.cb_sales_car.current(0)

        # Employees
        emp_list = [f"{e.employeeID} - {e.name} ({e.role})" for e in self.dealership.get_employees()]
        self.cb_sales_emp["values"] = emp_list
        if emp_list:
            self.cb_sales_emp.current(0)

    def process_sale_action(self):
        try:
            cust_val = self.cb_sales_cust.get()
            car_val = self.cb_sales_car.get()
            emp_val = self.cb_sales_emp.get()
            final_price = float(self.ent_sales_price.get())
            discount = float(self.ent_sales_disc.get() or 0.0)

            if not cust_val or not car_val or not emp_val:
                raise ValueError("Must select a Customer, Car, and Employee.")

            # Look up corresponding OOP objects
            cust_id = cust_val.split(" - ")[0]
            car_id = car_val.split(" - ")[0]
            emp_id = emp_val.split(" - ")[0]

            customer = next(c for c in self.dealership.get_customers() if c.customerID == cust_id)
            car = next(c for c in self.dealership.get_cars() if c.carID == car_id)
            employee = next(e for e in self.dealership.get_employees() if e.employeeID == emp_id)

            # Create Transaction Sale object
            sale_id = f"SALE-{str(uuid.uuid4())[:4].upper()}"
            sale = Sale(sale_id, car, customer, employee, final_price, discount)

            # Execute transaction in main Dealership controller
            self.dealership.record_sale(sale)

            # Update displays
            self.log_message(f"TRANS SUCCESS: {sale_id} processed by {employee.name}.")
            self.log_message(f"INVOICE PREVIEW:\nCar: {car.brand} {car.model}\nFinal Price: \${final_price:,.2f} + 8% tax.")
            self.log_message(f"Customer {customer.name} awarded points! Current total: {customer.loyaltyPoints}")

            self.populate_car_table()
            self.populate_customer_table()
            self.refresh_dashboard()
            self.refresh_sales_selectors()

            # Clean form
            self.ent_sales_price.delete(0, tk.END)
            self.ent_sales_disc.delete(0, tk.END)
            self.ent_sales_disc.insert(0, "0.0")

            invoice_info = (
                f"Invoice ID: {sale.saleID}\n"
                f"Date: {sale.date}\n"
                f"----------------------------------------\n"
                f"Car: {car.year} {car.brand} {car.model}\n"
                f"Customer: {customer.name}\n"
                f"Employee: {employee.name}\n"
                f"----------------------------------------\n"
                f"Subtotal: \${sale.finalPrice:,.2f}\n"
                f"Sales Tax (8%): \${sale.tax:,.2f}\n"
                f"========================================\n"
                f"TOTAL AMOUNT: \${sale.finalPrice + sale.tax:,.2f}\n"
                f"Profit Earned: \${sale.profit:,.2f}"
            )
            messagebox.showinfo("Invoice Processed", invoice_info)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to record sale: {str(e)}")


# ==============================================================================
# 3. MAIN EVENT LOOP
# ==============================================================================

if __name__ == "__main__":
    # Create the virtual Car Dealership which automatically links to SQLite and seeds
    app_dealership = CarDealership("Aero Luxe Dealership")

    # Initialize Tkinter Application
    app = DealershipGUI(app_dealership)
    app.mainloop()
