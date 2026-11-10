from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.products.models import Category, Product
from apps.inventory.models import RawMaterial, StockMovement
from apps.orders.models import Customer, Order, OrderItem, CustomCakeOrder
from apps.finance.models import AccountHead, Transaction, LedgerEntry
from apps.payroll.models import Employee, SalaryPayment
from apps.site_settings.models import SiteSetting


class Command(BaseCommand):
    help = 'Seeds initial professional bakery ERP data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Bakery ERP data..."))

        # 1. Site Settings
        setting, _ = SiteSetting.objects.get_or_create(id=1)
        setting.site_name = "BakeMaster Bakery & Confectionery"
        setting.contact_email = "support@bakemaster.com"
        setting.contact_phone = "+1 (800) 555-BAKE"
        setting.save()

        # 2. Categories
        categories_data = [
            ("Cakes & Special Orders", "Artisanal celebration cakes, layer cakes and wedding cakes"),
            ("Pastries & Tarts", "Fresh cream puffs, eclairs, fruit tarts and croissants"),
            ("Fresh Breads & Buns", "Sourdough, brioche, whole wheat, and dinner rolls"),
            ("Cookies & Biscuits", "Butter cookies, chocolate chip, macaroons, and biscotti"),
            ("Savory & Snacks", "Patties, savory quiches, chicken rolls, and sandwiches"),
            ("Coffee & Beverages", "Espresso, iced lattes, hot chocolate, and organic tea"),
        ]

        cat_objs = {}
        for name, desc in categories_data:
            c, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'is_active': True})
            cat_objs[name] = c

        # 3. Products
        products_data = [
            # Cakes
            ("Belgian Chocolate Fudge Cake (1 lb)", "Cakes & Special Orders", "CK-CHOC-01", 12.00, 24.00, 15, "pcs", 4),
            ("Red Velvet Cream Cheese Cake (1 lb)", "Cakes & Special Orders", "CK-RVEL-02", 14.00, 28.00, 10, "pcs", 4),
            ("Vanilla Fondant Celebration Cake (2 lbs)", "Cakes & Special Orders", "CK-VANI-03", 20.00, 45.00, 8, "pcs", 5),
            ("Black Forest Gateau (1 lb)", "Cakes & Special Orders", "CK-BLCK-04", 13.00, 26.00, 12, "pcs", 3),

            # Pastries
            ("French Butter Croissant", "Pastries & Tarts", "PST-CROI-01", 1.20, 3.50, 45, "pcs", 2),
            ("Chocolate Eclair", "Pastries & Tarts", "PST-ECLR-02", 1.80, 4.20, 30, "pcs", 2),
            ("Strawberry Custard Tart", "Pastries & Tarts", "PST-TART-03", 2.00, 4.80, 25, "pcs", 2),
            ("Blueberry Muffin", "Pastries & Tarts", "PST-MUFF-04", 1.10, 3.00, 40, "pcs", 3),

            # Breads
            ("Rustic Sourdough Loaf", "Fresh Breads & Buns", "BRD-SOUR-01", 2.50, 6.50, 20, "pcs", 4),
            ("Golden Brioche Loaf", "Fresh Breads & Buns", "BRD-BRIO-02", 3.00, 7.50, 18, "pcs", 4),
            ("Artisan Whole Wheat Bread", "Fresh Breads & Buns", "BRD-WWHT-03", 2.20, 5.50, 25, "pcs", 5),
            ("Garlic Butter Dinner Rolls (Pack of 6)", "Fresh Breads & Buns", "BRD-ROLL-04", 1.80, 4.50, 30, "pack", 3),

            # Cookies
            ("Choco-Chunk Cookies (Box of 6)", "Cookies & Biscuits", "CKI-CHOC-01", 3.50, 8.50, 35, "box", 14),
            ("French Almond Macarons (Assorted 6)", "Cookies & Biscuits", "CKI-MAC-02", 4.50, 12.00, 20, "box", 10),
            ("Danish Butter Cookies (250g)", "Cookies & Biscuits", "CKI-BUTR-03", 2.80, 7.00, 28, "pack", 30),

            # Savory
            ("Chicken Mushroom Puff Pastry", "Savory & Snacks", "SAV-CHIK-01", 1.50, 3.80, 32, "pcs", 2),
            ("Spiced Beef Empanada", "Savory & Snacks", "SAV-BEEF-02", 1.80, 4.50, 28, "pcs", 2),
            ("Spinach & Feta Quiche Slice", "Savory & Snacks", "SAV-QUIC-03", 2.10, 5.20, 22, "slice", 2),

            # Beverages
            ("Artisan Cappuccino", "Coffee & Beverages", "BEV-CAPP-01", 0.90, 4.00, 100, "pcs", 1),
            ("Iced Caramel Macchiato", "Coffee & Beverages", "BEV-ICED-02", 1.20, 4.80, 100, "pcs", 1),
        ]

        for name, cat_name, sku, cost, price, stock, unit, shelf in products_data:
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': cat_objs[cat_name],
                    'cost_price': Decimal(str(cost)),
                    'selling_price': Decimal(str(price)),
                    'stock_quantity': stock,
                    'unit': unit,
                    'shelf_life_days': shelf,
                    'is_active': True,
                }
            )

        # 4. Raw Materials & Stock
        raw_materials = [
            ("All-Purpose Flour (High Gluten)", "kg", 250.00, 30.00, 1.20, "Apex Millers Ltd"),
            ("Refined White Sugar", "kg", 180.00, 25.00, 1.10, "Sweet Harvest Co"),
            ("Unsalted Dairy Butter", "kg", 60.00, 15.00, 6.50, "Golden Valley Dairy"),
            ("Whole Fresh Milk", "liter", 80.00, 20.00, 1.40, "Meadow Farms"),
            ("Farm Fresh Eggs", "tray", 40.00, 10.00, 7.50, "Green Pasture Poultry"),
            ("Belgian Dark Cocoa Powder", "kg", 25.00, 5.00, 14.00, "Callebaut Importers"),
            ("Pure Vanilla Bean Extract", "liter", 8.00, 2.00, 45.00, "Madagascar Spices"),
            ("Instant Dry Yeast", "kg", 18.00, 4.00, 8.00, "Saf-Instant"),
            ("Cake Packaging Boxes (1 lb)", "box", 350.00, 50.00, 0.45, "Prime Packaging Corp"),
        ]

        for name, unit, stock, min_stock, cost, supplier in raw_materials:
            RawMaterial.objects.get_or_create(
                name=name,
                defaults={
                    'unit': unit,
                    'current_stock': Decimal(str(stock)),
                    'min_stock_alert': Decimal(str(min_stock)),
                    'unit_cost': Decimal(str(cost)),
                    'supplier_name': supplier
                }
            )

        # 5. Account Heads
        account_heads = [
            ("Counter POS Sales Revenue", "income", "Revenue from regular walk-in bakery sales"),
            ("Custom Cake Pre-Orders", "income", "Advance and delivery collections for custom celebration cakes"),
            ("Catering & Wholesale Orders", "income", "Corporate events and bulk bakery supply"),
            ("Raw Materials & Ingredients", "expense", "Flour, butter, sugar, eggs and baking essentials"),
            ("Employee Salaries & Wages", "expense", "Monthly remuneration for bakers, cashiers and staff"),
            ("Shop & Kitchen Rent", "expense", "Monthly commercial property rental"),
            ("Electricity, Gas & Utilities", "expense", "Oven power, refrigeration and gas burners"),
            ("Packaging & Disposables", "expense", "Cake boxes, pastry bags, cups and napkins"),
            ("Bakery Equipment Maintenance", "expense", "Oven servicing, mixer repairs, and tool upgrades"),
            ("Miscellaneous Operating Expenses", "expense", "General daily operational expenses"),
        ]

        head_objs = {}
        for name, h_type, desc in account_heads:
            h, _ = AccountHead.objects.get_or_create(
                name=name,
                defaults={'head_type': h_type, 'description': desc, 'is_active': True}
            )
            head_objs[name] = h

        # 6. Employees & Staff
        employees_data = [
            ("EMP-001", "Marcus Sterling", "Head Baker", "+1-555-0101", "marcus@bakemaster.com", 3800.00),
            ("EMP-002", "Elena Rostova", "Pastry Chef", "+1-555-0102", "elena@bakemaster.com", 3200.00),
            ("EMP-003", "David Kim", "Store Manager", "+1-555-0103", "david@bakemaster.com", 3000.00),
            ("EMP-004", "Sophia Martinez", "Cashier", "+1-555-0104", "sophia@bakemaster.com", 2100.00),
            ("EMP-005", "Jamal Crawford", "Kitchen Assistant", "+1-555-0105", "jamal@bakemaster.com", 1900.00),
        ]

        emp_objs = []
        for emp_id, name, desig, phone, email, salary in employees_data:
            emp, _ = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'name': name,
                    'designation': desig,
                    'phone': phone,
                    'email': email,
                    'basic_salary': Decimal(str(salary)),
                    'status': 'active'
                }
            )
            emp_objs.append(emp)

        # 7. Customers
        customers_data = [
            ("Emily Watson", "+1-555-9011", "emily.w@example.com", "742 Evergreen Terrace"),
            ("Robert Vance", "+1-555-9022", "robert.v@example.com", "144 Elm Street, Suite 4"),
            ("Jessica Alba", "+1-555-9033", "jessica@example.com", "221B Baker Street"),
            ("Michael Scott", "+1-555-9044", "michael.s@example.com", "1725 Slough Avenue"),
        ]

        cust_objs = []
        for name, phone, email, address in customers_data:
            cust, _ = Customer.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'email': email,
                    'address': address,
                    'total_orders': 3,
                    'total_spent': Decimal('185.00')
                }
            )
            cust_objs.append(cust)

        # 8. Sample Custom Cake Order
        today = timezone.now().date()
        cake_order, created = Order.objects.get_or_create(
            order_number="CAKE-20261110-SPEC1",
            defaults={
                'order_type': 'custom_cake',
                'customer': cust_objs[0],
                'status': 'baking',
                'payment_status': 'partial',
                'payment_method': 'card',
                'subtotal': Decimal('65.00'),
                'discount': Decimal('5.00'),
                'total_amount': Decimal('60.00'),
                'paid_amount': Decimal('30.00'),
                'due_amount': Decimal('30.00'),
                'notes': 'Gluten-free sponge requested if possible.'
            }
        )
        if created:
            CustomCakeOrder.objects.create(
                order=cake_order,
                flavor='Belgian Chocolate Truffle with Strawberry Ganache',
                weight_lbs=Decimal('3.0'),
                cake_message='Happy 10th Birthday Charlotte!',
                delivery_date=today + timedelta(days=1),
                tier_count=2,
                special_instructions='Pastel pink ribbons and edible pearls on the border.'
            )

        # 9. Seed Sample Transactions & Ledger
        sample_transactions = [
            ("Daily Counter Bakery Sales", "income", "Counter POS Sales Revenue", Decimal('1240.00'), 'cash'),
            ("Custom Birthday Cake Advance Collection", "income", "Custom Cake Pre-Orders", Decimal('350.00'), 'card'),
            ("Monthly Kitchen Electricity & Gas Bill", "expense", "Electricity, Gas & Utilities", Decimal('420.00'), 'bank'),
            ("Bakery Boxes & Disposable Packaging", "expense", "Packaging & Disposables", Decimal('180.00'), 'cash'),
            ("Emergency Oven Thermostat Repair", "expense", "Bakery Equipment Maintenance", Decimal('95.00'), 'cash'),
        ]

        if not Transaction.objects.exists():
            for title, t_type, head_name, amt, method in sample_transactions:
                Transaction.objects.create(
                    title=title,
                    transaction_type=t_type,
                    account_head=head_objs[head_name],
                    amount=amt,
                    payment_method=method,
                    date=today,
                    notes='System initial sample transaction'
                )

        # 10. Sample Salary Disbursal
        if not SalaryPayment.objects.exists() and emp_objs:
            for emp in emp_objs[:3]:
                SalaryPayment.objects.create(
                    employee=emp,
                    month_year="October 2026",
                    basic_salary=emp.basic_salary,
                    allowances=Decimal('150.00'),
                    overtime_pay=Decimal('80.00'),
                    deductions=Decimal('0.00'),
                    net_salary=emp.basic_salary + Decimal('230.00'),
                    payment_method='bank_transfer',
                    payment_status='paid',
                    payment_date=today - timedelta(days=5),
                    remarks="Paid via corporate payroll bank account."
                )

        self.stdout.write(self.style.SUCCESS("BakeMaster ERP data seeded successfully!"))
