# 🥖 Artisan Bakery Management System (BakeMaster ERP)

A modern, high-performance, enterprise-grade Bakery Management ERP software built with **Django 5, HTMX, Alpine.js, Tailwind CSS v4, and Django Unfold Admin**.

All user interfaces, reports, notifications, and code are strictly maintained in standard **English**.

---

## 📋 Comprehensive Project Roadmap & Execution Plan

### Phase 1: Environment & Foundation Setup
- [ ] Setup Python Virtual Environment (`venv`) & install dependencies from `requirements.txt`.
- [ ] Migrate database and verify Django Unfold Admin access.
- [ ] Clean up demo/legacy placeholder pages to strictly English UI.

### Phase 2: Core Bakery Catalog (`apps.products`)
- [ ] Product Categories (Cakes, Pastries, Breads, Cookies, Beverages, Savory).
- [ ] Product Model with SKU, Cost Price, Selling Price, Shelf Life (days), Unit of Measure, Image, and Active Status.
- [ ] Interactive HTMX-powered Product Catalog, Search, Filter, and CRUD modals.

### Phase 3: Raw Materials & Stock Management (`apps.inventory`)
- [ ] Raw Materials (Flour, Sugar, Butter, Dairy, Yeast, Packaging boxes, etc.).
- [ ] Stock In / Purchase logging and supplier linkage.
- [ ] Low Stock & Expiry automated alert system.
- [ ] Recipe / Bill of Materials (BOM) linking finished bakery goods to ingredients.

### Phase 4: Point of Sale (POS) & Custom Orders (`apps.orders`)
- [ ] **Counter POS Terminal**: Rapid touch-friendly billing, barcode/SKU support, instant receipt modal/printing.
- [ ] **Custom Cake & Bakery Pre-Orders**: Customization tracking (Flavors, Weight, Delivery Date & Time, Inscription/Message on Cake, Reference photo, Advance deposit, Delivery status).
- [ ] Customer Directory with purchase history and loyalty stats.

### Phase 5: Finance, Accounting & General Ledger (`apps.finance`)
- [ ] **Income & Expense Tracker**:
  - Income Categories (POS Sales, Custom Orders, Catering, Wholesale).
  - Expense Categories (Raw material purchase, Utility bills, Rent, Maintenance, Packaging).
  - Multi-payment accounts (Cash Drawer, Bank Account, Mobile Banking / Card).
- [ ] **General Ledger (Double-Entry Debit/Credit)**:
  - Account heads, transaction logs, automated journal entries for sales and expenses.
  - Customer & Vendor running ledger accounts (receivables and payables).
- [ ] **Financial Reports**:
  - Daily Sales & Cash Register Reconciliation.
  - Income vs Expense Statement.
  - Net Profit & Loss (P&L) calculation.

### Phase 6: Human Resources & Salary / Payroll (`apps.payroll`)
- [ ] Employee Profiles (Bakers, Chefs, Cashiers, Sales Representatives, Delivery Staff, Managers).
- [ ] Salary Structure (Basic Salary, Allowances, Overtime calculation, Deductions).
- [ ] Monthly Payroll Generation (Payslip generation, payment status: Pending, Paid, Partial).
- [ ] Auto-integration with Finance Expense & Cash/Bank ledger upon salary disbursement.

### Phase 7: Real-Time Executive Dashboard & UI Polishing
- [ ] Modern Analytics Dashboard with key performance indicators (KPIs):
  - Today's Total Sales & Net Revenue.
  - Today's Expenses & Net Profit.
  - Custom Cake orders pending for delivery today.
  - Critical Raw Material Stock alerts.
- [ ] Seamless HTMX navigation (`hx-boost`, zero page reloads, OOB Toasts).
- [ ] Dark Mode and Light Mode full compatibility.

---

## 🛠 Tech Stack & Architecture

- **Backend:** Python 3.12, Django 5.2.1
- **Admin Panel:** Django Unfold (Tailwind-based modern admin interface)
- **Frontend SPA Layer:** HTMX 1.27 + Alpine.js
- **Styling & Design System:** Tailwind CSS v4 (`django-tailwind-cli`)
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **State Management & Swaps:** Dynamic Base Template (`base_partial.html` / `base.html`) with Out-Of-Band (OOB) toasts.

---

## 🚀 Quick Start Guide

### 1. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations & Setup Admin
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` for the Bakery POS & Dashboard, and `http://127.0.0.1:8000/admin/` for the management console.
# bekary
