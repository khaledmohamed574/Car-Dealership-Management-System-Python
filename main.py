import uuid
from enum import Enum
from datetime import datetime, date
from typing import List, Dict, Optional, Union


# ==========================================
# ENUMERATIONS (From UML Diagram)
# ==========================================

class CarStatus(Enum):
    AVAILABLE = "Available"
    SOLD = "Sold"
    RESERVED = "Reserved"
    UNDER_MAINTENANCE = "UnderMaintenance"


class SaleStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    PENDING = "Pending"


class EmployeeStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "OnLeave"


class PaymentMethod(Enum):
    CASH = "Cash"
    CARD = "Card"
    BANK_TRANSFER = "BankTransfer"
    FINANCING = "Financing"
    CHECK = "Check"


class ExpenseType(Enum):
    RENT = "Rent"
    UTILITIES = "Utilities"
    SALARIES = "Salaries"
    MARKETING = "Marketing"
    MAINTENANCE = "Maintenance"
    OTHER = "Other"


class ReportType(Enum):
    SALES_REPORT = "SalesReport"
    PURCHASE_REPORT = "PurchaseReport"
    PROFIT_LOSS_REPORT = "ProfitLossReport"
    INVENTORY_REPORT = "InventoryReport"
    EXPENSE_REPORT = "ExpenseReport"


# ==========================================
# CLASS DEFINITIONS
# ==========================================

class MaintenanceRecord:
    def __init__(self, record_id: str, car_id: str, date_record: date, service_type: str, 
                 description: str, cost: float, next_service_date: date, performed_by: str):
        self.recordID: str = record_id
        self.carID: str = car_id
        self.date: date = date_record
        self.serviceType: str = service_type
        self.description: str = description
        self.cost: float = cost
        self.nextServiceDate: date = next_service_date
        self.performedBy: str = performed_by

    @staticmethod
    def add_record(car_dealership, record: 'MaintenanceRecord') -> None:
        car = next((c for c in car_dealership.cars if c.carID == record.carID), None)
        if car and isinstance(car, UsedCar):
            car.add_maintenance(record)
            print(f"[MAINTENANCE] Record {record.recordID} added successfully for vehicle {car.brand} {car.model}.")
        else:
            print(f"[MAINTENANCE] Error: Car ID {record.carID} not found or not a UsedCar.")

    @staticmethod
    def get_history(car_dealership, car_id: str) -> List['MaintenanceRecord']:
        car = next((c for c in car_dealership.cars if c.carID == car_id), None)
        if car:
            print(f"[MAINTENANCE] Retrieved {len(car.maintenance_records)} records for car ID {car_id}.")
            return car.maintenance_records
        print(f"[MAINTENANCE] Car ID {car_id} not found in database.")
        return []

    def __str__(self) -> str:
        return f"[{self.date}] {self.serviceType} - Cost: \${self.cost:,.2f} (Next due: {self.nextServiceDate})"


class Insurance:
    def __init__(self, insurance_id: str, car_id: str, provider: str, policy_number: str, 
                 start_date: date, end_date: date, coverage_details: str, premium: float):
        self.insuranceID: str = insurance_id
        self.carID: str = car_id
        self.provider: str = provider
        self.policyNumber: str = policy_number
        self.startDate: date = start_date
        self.endDate: date = end_date
        self.coverageDetails: str = coverage_details
        self.premium: float = premium

    @staticmethod
    def add_insurance(car_dealership, insurance: 'Insurance') -> None:
        car = next((c for c in car_dealership.cars if c.carID == insurance.carID), None)
        if car:
            car.insurance_policies.append(insurance)
            print(f"[INSURANCE] Policy {insurance.policyNumber} successfully linked to {car.brand} {car.model}.")
        else:
            print(f"[INSURANCE] Error: Car ID {insurance.carID} not found.")

    def is_active(self) -> bool:
        today = date.today()
        active = self.startDate <= today <= self.endDate
        print(f"[INSURANCE] Checking status of policy {self.policyNumber} on {today}: {'ACTIVE' if active else 'EXPIRED'}")
        return active


class Document:
    def __init__(self, document_id: str, car_id: str, document_type: str, file_path: str, 
                 upload_date: date, uploaded_by: str):
        self.documentID: str = document_id
        self.carID: str = car_id
        self.documentType: str = document_type
        self.filePath: str = file_path
        self.uploadDate: date = upload_date
        self.uploadedBy: str = uploaded_by

    def upload_document(self, car_dealership) -> None:
        car = next((c for c in car_dealership.cars if c.carID == self.carID), None)
        if car:
            car.documents.append(self)
            print(f"[DOCUMENT] Document {self.documentID} ({self.documentType}) successfully uploaded for {car.brand} {car.model}.")
        else:
            print(f"[DOCUMENT] Error: Car ID {self.carID} not found.")

    def view_document(self) -> str:
        print(f"[DOCUMENT] Viewing '{self.documentType}' from location: {self.filePath} (uploaded by {self.uploadedBy})")
        return self.filePath

    def delete_document(self, car_dealership) -> None:
        car = next((c for c in car_dealership.cars if c.carID == self.carID), None)
        if car and self in car.documents:
            car.documents.remove(self)
            print(f"[DOCUMENT] Document {self.documentID} successfully deleted.")
        else:
            print(f"[DOCUMENT] Error: Document {self.documentID} not found on car.")


class Car:
    def __init__(self, car_id: str, stock_number: str, brand: str, model: str, category: str, 
                 body_type: str, year: int, color: str, vin: str, fuel_type: str, 
                 transmission: str, drive_train: str, engine_size: str, horsepower: int, 
                 torque: int, mileage: int, condition: str, status: CarStatus, 
                 purchase_price: float, selling_price: float, market_price: float, 
                 description: str, number_of_owners: int, accident_history: str, 
                 service_history: str, warranty: str, registration_date: date, location: str):
        self.carID: str = car_id
        self.stockNumber: str = stock_number
        self.brand: str = brand
        self.model: str = model
        self.category: str = category
        self.bodyType: str = body_type
        self.year: int = year
        self.color: str = color
        self.VIN: str = vin
        self.fuelType: str = fuel_type
        self.transmission: str = transmission
        self.driveTrain: str = drive_train
        self.engineSize: str = engine_size
        self.horsepower: int = horsepower
        self.torque: int = torque
        self.mileage: int = mileage
        self.condition: str = condition  # e.g., "New" or "Used"
        self.status: CarStatus = status
        self.purchasePrice: float = purchase_price
        self.sellingPrice: float = selling_price
        self.marketPrice: float = market_price
        self.description: str = description
        self.numberOfOwners: int = number_of_owners
        self.accidentHistory: str = accident_history
        self.serviceHistory: str = service_history
        self.warranty: str = warranty
        self.registrationDate: date = registration_date
        self.location: str = location
        
        # Associated objects (0..*)
        self.maintenance_records: List[MaintenanceRecord] = []
        self.insurance_policies: List[Insurance] = []
        self.documents: List[Document] = []

    def update_price(self, price: float) -> None:
        self.sellingPrice = price
        print(f"[VEHICLE] Price for {self.brand} {self.model} updated to \${price:,.2f}")

    def update_status(self, status: CarStatus) -> None:
        self.status = status
        print(f"[VEHICLE] Status for {self.brand} {self.model} set to {status.value}")

    def calculate_profit(self) -> float:
        return self.sellingPrice - self.purchasePrice

    def is_available(self) -> bool:
        return self.status == CarStatus.AVAILABLE


class NewCar(Car):
    def __init__(self, car_id: str, stock_number: str, brand: str, model: str, category: str, 
                 body_type: str, year: int, color: str, vin: str, fuel_type: str, 
                 transmission: str, drive_train: str, engine_size: str, horsepower: int, 
                 torque: int, mileage: int, status: CarStatus, purchase_price: float, 
                 selling_price: float, market_price: float, description: str, 
                 warranty_period: int, delivery_date: date, is_certified: bool, 
                 manufacturer_warranty: str):
        super().__init__(car_id, stock_number, brand, model, category, body_type, year, color, vin, 
                         fuel_type, transmission, drive_train, engine_size, horsepower, torque, 
                         mileage, "New", status, purchase_price, selling_price, market_price, 
                         description, 0, "None", "Factory Delivery", f"{warranty_period} Months", 
                         delivery_date, "Showroom Floor")
        self.manufacturer: str = brand
        self.manufacturerWarranty: str = manufacturer_warranty
        self.warrantyPeriod: int = warranty_period  # months
        self.deliveryDate: date = delivery_date
        self.isCertified: bool = is_certified

    def extend_warranty(self, months: int) -> None:
        self.warrantyPeriod += months
        self.warranty = f"{self.warrantyPeriod} Months"
        print(f"[NEWCAR] Warranty extended by {months} months. New total: {self.warrantyPeriod} months.")


class UsedCar(Car):
    def __init__(self, car_id: str, stock_number: str, brand: str, model: str, category: str, 
                 body_type: str, year: int, color: str, vin: str, fuel_type: str, 
                 transmission: str, drive_train: str, engine_size: str, horsepower: int, 
                 torque: int, mileage: int, status: CarStatus, purchase_price: float, 
                 selling_price: float, market_price: float, description: str, 
                 number_of_owners: int, accident_history: str, service_history: str, 
                 warranty: str, registration_date: date, location: str,
                 previous_owners: int, kilometers_driven: int, inspection_report: str, 
                 last_service_date: date, next_service_date: date, is_certified_used: bool):
        super().__init__(car_id, stock_number, brand, model, category, body_type, year, color, vin, 
                         fuel_type, transmission, drive_train, engine_size, horsepower, torque, 
                         mileage, "Used", status, purchase_price, selling_price, market_price, 
                         description, number_of_owners, accident_history, service_history, 
                         warranty, registration_date, location)
        self.previousOwners: int = previous_owners
        self.kilometersDriven: int = kilometers_driven
        self.inspectionReport: str = inspection_report
        self.lastServiceDate: date = last_service_date
        self.nextServiceDate: date = next_service_date
        self.isCertifiedUsed: bool = is_certified_used

    def add_maintenance(self, record: MaintenanceRecord) -> None:
        self.maintenance_records.append(record)
        self.lastServiceDate = record.date
        self.nextServiceDate = record.nextServiceDate
        print(f"[USEDCAR] Maintenance record logged for {self.brand} {self.model}. Next service: {self.nextServiceDate}")


class Employee:
    def __init__(self, employee_id: str, name: str, role: str, salary: float, phone: str, 
                 email: str, hire_date: date, address: str, status: EmployeeStatus, 
                 username: str):
        self.employeeID: str = employee_id
        self.name: str = name
        self.role: str = role
        self.salary: float = salary
        self.phone: str = phone
        self.email: str = email
        self.hireDate: date = hire_date
        self.address: str = address
        self.status: EmployeeStatus = status
        self.username: str = username
        self.passwordHash: str = "pbkdf2:sha256:default_hashed_pass"

    def add_car(self, car_dealership, car: Car) -> None:
        car_dealership.add_car(car)
        print(f"[EMPLOYEE] {self.name} registered vehicle {car.brand} {car.model} into dealership inventory.")


class Manager(Employee):
    def __init__(self, employee_id: str, name: str, salary: float, phone: str, email: str, 
                 hire_date: date, address: str, status: EmployeeStatus, username: str, 
                 department: str):
        super().__init__(employee_id, name, "Manager", salary, phone, email, hire_date, address, 
                         status, username)
        self.department: str = department

    def approve_sale(self, sale) -> None:
        print(f"[MANAGER] Sarah Jenkins approved Sale ID {sale.saleID} on {date.today()}.")

    def approve_purchase(self, purchase) -> None:
        print(f"[MANAGER] Sarah Jenkins approved Supplier Purchase ID {purchase.purchaseID}.")

    def generate_financial_report(self, car_dealership) -> 'Report':
        report = car_dealership.generate_report(ReportType.PROFIT_LOSS_REPORT, self)
        print(f"[MANAGER] Generated profit & loss Report ID: {report.reportID}.")
        return report

    def manage_employees(self, car_dealership, action: str, target_emp: Employee) -> None:
        if action == "promote":
            target_emp.salary *= 1.15
            print(f"[MANAGER] Promoted {target_emp.name}. New salary: \${target_emp.salary:,.2f}.")
        elif action == "terminate":
            target_emp.status = EmployeeStatus.INACTIVE
            print(f"[MANAGER] Changed status of {target_emp.name} to INACTIVE.")
        elif action == "suspend":
            target_emp.status = EmployeeStatus.ON_LEAVE
            print(f"[MANAGER] Placed {target_emp.name} on OnLeave status.")

    def system_settings(self, config_key: str, config_value: str) -> None:
        print(f"[MANAGER-SETTINGS] Config key '{config_key}' updated to value '{config_value}' by Sarah Jenkins.")


class Customer:
    def __init__(self, customer_id: str, name: str, phone: str, email: str, address: str, 
                 national_id: str, register_date: date, loyalty_points: int = 0, notes: str = ""):
        self.customerID: str = customer_id
        self.name: str = name
        self.phone: str = phone
        self.email: str = email
        self.address: str = address
        self.nationalID: str = national_id
        self.registerDate: date = register_date
        self.loyaltyPoints: int = loyalty_points
        self.notes: str = notes
        
        self.favorites: List[Car] = []
        self.purchase_history: List['Sale'] = []

    def buy_car(self, sale) -> None:
        if sale not in self.purchase_history:
            self.purchase_history.append(sale)
        earned = int(sale.finalPrice / 100)
        self.loyaltyPoints += earned
        print(f"[CUSTOMER] Recorded purchase of {sale.car.brand} {sale.car.model} for {self.name}. Earned {earned} loyalty points. Current Total: {self.loyaltyPoints}.")

    def view_purchase_history(self) -> List['Sale']:
        print(f"[CUSTOMER] Retrieving purchase ledger for {self.name}. Total sales found: {len(self.purchase_history)}.")
        return self.purchase_history

    def update_info(self, phone: str, email: str, address: str) -> None:
        self.phone = phone
        self.email = email
        self.address = address
        print(f"[CUSTOMER] Updated contact particulars for customer {self.name} successfully.")

    def add_to_favorites(self, car: Car) -> None:
        if car not in self.favorites:
            self.favorites.append(car)
            print(f"[CUSTOMER] Added vehicle {car.brand} {car.model} (Stock: {car.stockNumber}) to favorites for {self.name}.")


class Payment:
    def __init__(self, payment_id: str, sale_id: str, amount: float, method: PaymentMethod, 
                 payment_date: date, reference_number: str, received_by: Employee):
        self.paymentID: str = payment_id
        self.saleID: str = sale_id
        self.amount: float = amount
        self.method: PaymentMethod = method
        self.date: date = payment_date
        self.referenceNumber: str = reference_number
        self.receivedBy: Employee = received_by

    def validate(self) -> bool:
        if self.amount <= 0:
            print(f"[PAYMENT] Validation Failed: Non-positive amount.")
            return False
        if not self.referenceNumber:
            print(f"[PAYMENT] Validation Failed: Missing reference number.")
            return False
        print(f"[PAYMENT] Policy Validation Succeeded for payment ref {self.referenceNumber}.")
        return True


class Sale:
    def __init__(self, sale_id: str, sale_date: date, car: Car, customer: Customer, 
                 employee: Employee, payment_method: PaymentMethod, final_price: float, 
                 discount: float, tax_rate: float = 0.08, notes: str = ""):
        self.saleID: str = sale_id
        self.date: date = sale_date
        self.car: Car = car
        self.customer: Customer = customer
        self.employee: Employee = employee
        self.paymentMethod: PaymentMethod = payment_method
        self.finalPrice: float = final_price
        self.discount: float = discount
        self.tax: float = final_price * tax_rate
        self.notes: str = notes
        self.status: SaleStatus = SaleStatus.PENDING
        
        self.payments: List[Payment] = []
        self.profit: float = self.calculate_profit()

    def calculate_profit(self) -> float:
        return self.finalPrice - self.car.purchasePrice

    def print_invoice(self) -> str:
        return (f"========================================\n"
                f"            SALES INVOICE               \n"
                f"Invoice ID: {self.saleID}   Date: {self.date}\n"
                f"----------------------------------------\n"
                f"Car: {self.car.year} {self.car.brand} {self.car.model}\n"
                f"Stock #: {self.car.stockNumber}\n"
                f"----------------------------------------\n"
                f"Customer: {self.customer.name}\n"
                f"Sales Agent: {self.employee.name}\n"
                f"----------------------------------------\n"
                f"Retail Value:   \${self.car.sellingPrice:,.2f}\n"
                f"Discount:      -\${self.discount:,.2f}\n"
                f"Subtotal:       \${self.finalPrice:,.2f}\n"
                f"Sales Tax (8%): \${self.tax:,.2f}\n"
                f"========================================\n"
                f"TOTAL AMOUNT:   \${self.finalPrice + self.tax:,.2f}\n"
                f"Payment Method: {self.paymentMethod.value}\n"
                f"Status:         {self.status.value}\n"
                f"========================================\n")

    def cancel_sale(self) -> None:
        self.status = SaleStatus.CANCELLED
        self.car.update_status(CarStatus.AVAILABLE)
        print(f"[SALE] Sale {self.saleID} has been cancelled. Car is now available.")

    def add_payment(self, payment: Payment) -> None:
        if payment.validate():
            self.payments.append(payment)
            paid_sum = sum(p.amount for p in self.payments)
            if paid_sum >= (self.finalPrice + self.tax):
                self.status = SaleStatus.COMPLETED
                self.car.update_status(CarStatus.SOLD)
                self.customer.buy_car(self)
                print(f"[SALE] Full payment received for Sale {self.saleID}. Sale Completed.")
            else:
                print(f"[SALE] Partial payment received: \${paid_sum:,.2f} of \${self.finalPrice + self.tax:,.2f} paid.")


class ExpenseCategory:
    def __init__(self, category_id: str, name: str, description: str):
        self.categoryID: str = category_id
        self.name: str = name
        self.description: str = description

    @staticmethod
    def add_category(car_dealership, category: 'ExpenseCategory') -> None:
        print(f"[EXPENSE-CATEGORY] New category '{category.name}' registered: {category.description}")


class Expense:
    def __init__(self, expense_id: str, expense_type: ExpenseType, amount: float, 
                 expense_date: date, description: str, paid_by: Employee, attachment: str = ""):
        self.expenseID: str = expense_id
        self.type: ExpenseType = expense_type
        self.amount: float = amount
        self.date: date = expense_date
        self.description: str = description
        self.paidBy: Employee = paid_by
        self.attachment: str = attachment

    def add_expense(self, car_dealership) -> None:
        car_dealership.add_expense(self)
        print(f"[EXPENSE] Expense {self.expenseID} for \${self.amount:,.2f} logged successfully.")

    @staticmethod
    def view_expenses(car_dealership) -> List['Expense']:
        print(f"[EXPENSE] Retrieving dealership expenses. Total expenditures: {len(car_dealership.expenses)}.")
        return car_dealership.expenses

    def delete_expense(self, car_dealership) -> None:
        if self in car_dealership.expenses:
            car_dealership.expenses.remove(self)
            car_dealership.totalExpenses -= self.amount
            print(f"[EXPENSE] Deleted expense {self.expenseID} for \${self.amount:,.2f}.")
        else:
            print(f"[EXPENSE] Error: Expense {self.expenseID} not found.")


class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_person: str, phone: str, 
                 email: str, address: str, rating: float):
        self.supplierID: str = supplier_id
        self.name: str = name
        self.contactPerson: str = contact_person
        self.phone: str = phone
        self.email: str = email
        self.address: str = address
        self.rating: float = rating

    def supply_cars(self, car_dealership, cars: List[Car], manager: Manager) -> None:
        for car in cars:
            purchase = Purchase(f"PUR-{str(uuid.uuid4())[:4].upper()}", self, car, date.today(), car.purchasePrice)
            manager.approve_purchase(purchase)
            car_dealership.buy_car(purchase)
        print(f"[SUPPLIER] {self.name} supplied {len(cars)} vehicles to dealership inventory.")

    def view_supplied_cars(self, car_dealership) -> List[Car]:
        print(f"[SUPPLIER] Fetching supplied car ledger for supplier {self.name}...")
        return [c for c in car_dealership.cars if c.purchasePrice > 0]


class Purchase:
    def __init__(self, purchase_id: str, supplier: Supplier, car: Car, 
                 purchase_date: date, cost: float, notes: str = ""):
        self.purchaseID: str = purchase_id
        self.supplier: Supplier = supplier
        self.car: Car = car
        self.purchaseDate: date = purchase_date
        self.cost: float = cost
        self.notes: str = notes
        self.status: str = "Pending"

    def record_purchase(self) -> None:
        self.status = "Completed"
        self.car.update_status(CarStatus.AVAILABLE)
        print(f"[PURCHASE] Dealership acquired {self.car.brand} {self.car.model} from {self.supplier.name} for \${self.cost:,.2f}.")

    def calculate_total(self) -> float:
        total = self.cost * 1.05  # Standard dealer surcharge
        print(f"[PURCHASE] Calculated total acquisition cost (with shipping): \${total:,.2f}")
        return total

    def cancel_purchase(self) -> None:
        self.status = "Cancelled"
        print(f"[PURCHASE] Purchase ID {self.purchaseID} from {self.supplier.name} was CANCELLED.")


class Report:
    def __init__(self, report_id: str, report_type: ReportType, from_date: date, to_date: date, 
                 generated_by: Employee):
        self.reportID: str = report_id
        self.type: ReportType = report_type
        self.fromDate: date = from_date
        self.toDate: date = to_date
        self.generatedBy: Employee = generated_by
        self.generatedOn: datetime = datetime.now()
        self.filePath: str = f"/reports/{report_type.value.lower()}_{report_id}.txt"

    def generate(self, dealership) -> str:
        report_str = f"REPORT: {self.type.value}\nGenerated by: {self.generatedBy.name} on {self.generatedOn}\n"
        report_str += f"Reporting Period: {self.fromDate} to {self.toDate}\n"
        report_str += "="*40 + "\n"
        
        if self.type == ReportType.SALES_REPORT:
            report_str += f"Total Completed Sales: {len([s for s in dealership.sales if s.status == SaleStatus.COMPLETED])}\n"
            for sale in dealership.sales:
                report_str += f"- Sale ID: {sale.saleID} | Car: {sale.car.brand} {sale.car.model} | Customer: {sale.customer.name} | Total: \${sale.finalPrice:,.2f}\n"
        elif self.type == ReportType.PROFIT_LOSS_REPORT:
            profit = dealership.calculate_profit()
            expenses = dealership.calculate_expenses()
            report_str += f"Gross Profits: \${profit:,.2f}\n"
            report_str += f"Total Expenses: \${expenses:,.2f}\n"
            report_str += f"Net P/L: \${profit - expenses:,.2f}\n"
            
        return report_str

    def export(self, format_type: str) -> str:
        print(f"[REPORT-EXPORT] Exported report {self.reportID} successfully to format: {format_type.upper()}. File saved: {self.filePath}.{format_type.lower()}")
        return f"{self.filePath}.{format_type.lower()}"


class CarDealership:
    def __init__(self, name: str, address: str, phone: str, email: str, logo: str):
        self.name: str = name
        self.address: str = address
        self.phone: str = phone
        self.email: str = email
        self.logo: str = logo
        self.openingDate: date = date.today()
        
        # Lists (0..*)
        self.cars: List[Car] = []
        self.employees: List[Employee] = []
        self.customers: List[Customer] = []
        self.sales: List[Sale] = []
        self.expenses: List[Expense] = []
        
        self.totalProfit: float = 0.0
        self.totalLoss: float = 0.0
        self.totalExpenses: float = 0.0

    def add_car(self, car: Car) -> None:
        self.cars.append(car)

    def remove_car(self, car_id: str) -> None:
        self.cars = [c for c in self.cars if c.carID != car_id]
        print(f"[DEALERSHIP] Vehicle ID {car_id} removed from dealership database.")

    def search_cars(self, criteria: Dict[str, Union[str, int]]) -> List[Car]:
        results = self.cars
        for key, val in criteria.items():
            if hasattr(Car, key):
                results = [c for c in results if getattr(c, key) == val]
        print(f"[DEALERSHIP] Searched showroom inventory using criteria {criteria}. Matches found: {len(results)}.")
        return results

    def register_employee(self, emp: Employee) -> None:
        self.employees.append(emp)

    def register_customer(self, cus: Customer) -> None:
        self.customers.append(cus)

    def sell_car(self, sale: Sale) -> None:
        self.sales.append(sale)
        if sale.status == SaleStatus.COMPLETED:
            self.totalProfit += sale.profit

    def buy_car(self, purchase: Purchase) -> None:
        self.cars.append(purchase.car)
        purchase.record_purchase()

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)
        self.totalExpenses += expense.amount

    def calculate_profit(self) -> float:
        return sum(sale.profit for sale in self.sales if sale.status == SaleStatus.COMPLETED)

    def calculate_loss(self) -> float:
        return sum(sale.discount for sale in self.sales if sale.status == SaleStatus.COMPLETED)

    def calculate_expenses(self) -> float:
        return sum(e.amount for e in self.expenses)

    def generate_report(self, report_type: ReportType, generated_by: Employee) -> Report:
        rep = Report(str(uuid.uuid4())[:8], report_type, self.openingDate, date.today(), generated_by)
        print(f"[DEALERSHIP] Generated {report_type.value} report. File path: {rep.filePath}.")
        return rep

    def get_dashboard_data(self) -> Dict:
        available_cars = len([c for c in self.cars if c.is_available()])
        sold_cars = len([c for c in self.cars if c.status == CarStatus.SOLD])
        active_staff = len([e for e in self.employees if e.status == EmployeeStatus.ACTIVE])
        gross_profit = self.calculate_profit()
        expenses = self.calculate_expenses()
        net = gross_profit - expenses
        
        return {
            "Dealership Name": self.name,
            "Total Inventory Count": len(self.cars),
            "Available Vehicles": available_cars,
            "Sold Vehicles": sold_cars,
            "Active Employees": active_staff,
            "Gross Revenue/Profit": gross_profit,
            "Operating Expenses": expenses,
            "Net Earnings": net
        }


# ==========================================
# SIMULATION INVOCATION ENGINE
# ==========================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("   CAR DEALERSHIP MANAGEMENT SYSTEM - OOP RUNTIME")
    print("="*50)
    
    # 1. Instantiate the Dealership
    dealership = CarDealership(
        name="Aero Luxe Dealership", 
        address="100 Grand Horizon Parkway, SF", 
        phone="+1 (555) LUX-CARS", 
        email="info@aeroluxe.com", 
        logo="logo.png"
    )
    
    # 2. Register Staff members
    manager = Manager(
        employee_id="EMP-100",
        name="Sarah Jenkins",
        salary=95000.0,
        phone="+1-555-0011",
        email="sarah@aeroluxe.com",
        hire_date=date(2021, 1, 15),
        address="100 Grand Horizon Parkway, SF",
        status=EmployeeStatus.ACTIVE,
        username="sjenkins",
        department="Executive Administration"
    )
    sales_rep = Employee(
        employee_id="EMP-101",
        name="Marcus Vance",
        role="Sales Agent",
        salary=50000.0,
        phone="+1-555-0022",
        email="marcus@aeroluxe.com",
        hire_date=date(2022, 5, 10),
        address="100 Grand Horizon Parkway, SF",
        status=EmployeeStatus.ACTIVE,
        username="mvance"
    )
    dealership.register_employee(manager)
    dealership.register_employee(sales_rep)
    
    # 3. Setup a Supplier and acquire a car (Purchase & Supplier relation)
    supplier = Supplier("SUP-001", "Global Prestige Exports", "Hans Mueller", "+49 711 5002", "hans@prestige.de", "Stuttgart, DE", 4.9)
    raw_car_used = UsedCar(
        car_id="CAR-002", stock_number="STK-3810", brand="Porsche", model="911 Carrera S", 
        category="Sports", body_type="Coupe", year=2022, color="Guards Red", vin="WP0AB2A92NSXXXXXX", 
        fuel_type="Gasoline", transmission="PDK 8-speed", drive_train="RWD", engine_size="3.0L Flat-6", 
        horsepower=443, torque=390, mileage=12500, status=CarStatus.AVAILABLE, purchase_price=110000, 
        selling_price=124900, market_price=128000, description="Flawless Porsche Carrera.", 
        number_of_owners=1, accident_history="None", service_history="Porsche certified", 
        warranty="12M dealership warranty", registration_date=date(2022, 3, 15), location="Premium Bay",
        previous_owners=1, kilometers_driven=20116, inspection_report="Pass", last_service_date=date(2024, 2, 10),
        next_service_date=date(2025, 2, 10), is_certified_used=True
    )
    
    purchase = Purchase("PUR-500", supplier, raw_car_used, date(2024, 2, 15), 110000.0, "Acquired mint-condition model.")
    manager.approve_purchase(purchase)
    dealership.buy_car(purchase)
    
    # 4. Add a brand new car directly (NewCar relation)
    new_tesla = NewCar(
        car_id="CAR-001", stock_number="STK-4591", brand="Tesla", model="Model Y", 
        category="SUV", body_type="SUV", year=2024, color="Solid Black", vin="5YJYGDEE7RFXXXXXX", 
        fuel_type="Electric", transmission="Automatic", drive_train="AWD", engine_size="Dual Motor", 
        horsepower=384, torque=376, mileage=15, status=CarStatus.AVAILABLE, purchase_price=42000, 
        selling_price=48990, market_price=49500, description="Brand new EV direct from Fremont.", 
        warranty_period=48, delivery_date=date(2024, 5, 8), is_certified=True, manufacturer_warranty="Factory Standard"
    )
    sales_rep.add_car(dealership, new_tesla)
    
    # 5. Register a Customer
    vip_customer = Customer("CUST-001", "Bruce Wayne", "+1-555-7777", "bruce@waynecorp.com", "Wayne Manor, Gotham", "SSN-001-001", date(2020, 5, 12))
    dealership.register_customer(vip_customer)
    vip_customer.add_to_favorites(raw_car_used)
    
    # 6. Execute a Sale transaction
    print("\n--- INITIATING TRANSACTION ---")
    sale = Sale(
        sale_id="SALE-770", sale_date=date(2024, 6, 20), car=raw_car_used, customer=vip_customer, 
        employee=sales_rep, payment_method=PaymentMethod.BANK_TRANSFER, final_price=124900.0, discount=0.0
    )
    dealership.sell_car(sale)
    print(sale.print_invoice())
    
    # 7. Record a Payment (validate & auto-upgrade sale status & mark car sold)
    payment = Payment("PAY-992", sale.saleID, 134892.0, PaymentMethod.BANK_TRANSFER, date(2024, 6, 20), "WIRE-REF-88301", sales_rep) # Includes 8% tax
    sale.add_payment(payment)
    
    # 8. Record some Operating Expenses
    dealership.add_expense(Expense("EXP-01", ExpenseType.RENT, 12000.0, date(2024, 7, 1), "Facility lease", manager))
    dealership.add_expense(Expense("EXP-02", ExpenseType.UTILITIES, 850.0, date(2024, 7, 5), "Facility Power", manager))
    
    # 9. Log standard maintenance on remaining vehicle
    maintenance = MaintenanceRecord("MNT-01", new_tesla.carID, date(2024, 7, 12), "Factory Ceramic Coating", "Showroom detailing & hydrophobic sealing", 450.0, date(2025, 7, 12), "Detailing Dept")
    new_tesla.update_status(CarStatus.UNDER_MAINTENANCE)
    
    # 10. Dashboard analytics printout
    print("\n" + "="*50)
    print("   DEALERSHIP EXECUTIVE REAL-TIME DASHBOARD")
    print("="*50)
    dash_data = dealership.get_dashboard_data()
    for key, val in dash_data.items():
        if isinstance(val, float):
            print(f"{key:<30}: \${val:,.2f}")
        else:
            print(f"{key:<30}: {val}")
    print("="*50 + "\n")
