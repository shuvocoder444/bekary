# 🥖 Artisan Bakery Management System (BakeMaster ERP)

A modern, high-performance, enterprise-grade Bakery Management ERP software built with **Django, HTMX, Alpine.js, Tailwind CSS v4, and Django Unfold Admin**.

---

## 🏭 Bakery Production, Raw Materials & Hawker Distribution Roadmap

### 1. Raw Materials Stock & Inventory
- **Raw Materials Catalog (`RawMaterial`)**: Soybean Oil, Eggs, Flour, Sugar, Yeast, Butter, Flavoring, etc.
- **Measurement Units (`Units`)**: Kilogram (kg), Gram (g), Liter (L), Piece (pcs), Box, Bag.
- **Stock Movements & Purchases (`StockMovement - Purchase`)**: Record purchases with invoice/voucher reference, supplier, quantity received, unit cost, and total expenses.
- **Automatic Stock Tracking**: Real-time balance calculations, low-stock threshold alerts, and reorder levels.

### 2. Baking Production & Batch Recipe BOM
- **Production Batches (`ProductionBatch`)**: Batch identifier (e.g., `BATCH-20261110-001`), production date, baker notes, and status.
- **Bill of Materials Consumption (`BatchConsumption`)**:
  - Exact raw material consumption per baking session (e.g., 2 kg Oil, 4 pcs Eggs, 30 kg Flour).
  - Automatically deducts stock from `RawMaterial` inventory upon batch confirmation.
- **Finished Goods Output (`BatchOutput`)**:
  - Quantity of finished bakery goods produced (e.g., 40 pcs Milk Bread, 15 pcs Chocolate Cake).
  - Automatically adds finished quantities to `Product.stock_quantity`.
- **Cost Calculation (BOM Unit Cost)**: Automatically divides total consumed ingredient cost across produced units to calculate the accurate cost per piece.

### 3. Production & Ingredient Consumption Reports
- **Date Range Filters**: Daily, weekly, monthly, or custom date-range production analytics.
- **Ingredient Usage Breakdown**: Aggregated consumption of flour, oil, sugar, eggs, and other ingredients over the selected period.
- **Output Production Breakdown**: Summary of total pieces baked for each product catalog item.
- **Detailed Batch Audit**: Complete drill-down of every production run, including ingredient costs, output yields, and timestamps.
- **Printable Reports**: Formatted print view optimized for daily bakery log sheets.

### 4. Hawker & Route Distribution (Delivery Challans)
- **Hawker & Dealer Profiles (`Customer - type: hawker`)**: Dedicated delivery agent accounts with phone numbers, designated routes, and areas.
- **Delivery Challans (`Order / Hawker Dispatch`)**:
  - Issue finished products to hawkers for morning/evening distribution runs (e.g., 20 pcs Bread @ ৳70, 5 pcs Cake @ ৳750).
  - Automatically deducts dispatched quantities from finished product inventory.
  - Multi-item line entries with customizable distributor pricing.
- **Settlement & Cash Collection**:
  - Record cash and digital payments received upon delivery dispatch.
  - Automatically calculates remaining balance and posts it to the hawker's running due ledger.

### 5. Hawker Due Ledger & Sales Reports
- **Sales & Distribution History**: Comprehensive tracking of what items and quantities each hawker received.
- **Running Due Ledger**: Outstanding balances, total challan bill amounts, and lifetime collections per hawker.
- **Thermal Receipt & Challan Invoices**: One-click printable delivery challan receipts with detailed product breakdowns and payment summaries.

---

## 🛠 Tech Stack & Architecture

- **Backend:** Python 3.12, Django 5.2 / 6.0
- **Admin Panel:** Django Unfold (Tailwind-based modern admin interface)
- **Frontend SPA Layer:** HTMX 1.27+ & Alpine.js
- **Styling & Design System:** Tailwind CSS v4 (`django-tailwind-cli`)
- **Database:** SQLite / PostgreSQL (Production ready)
- **State Management & Swaps:** Dynamic Base Template (`base_partial.html` / `base.html`) with Out-Of-Band (OOB) toasts.

---

## 🚀 Deployment & Live Access

- **Live URL:** [https://bekary.velohoster.com](https://bekary.velohoster.com)
- **POS Billing Counter:** [https://bekary.velohoster.com/pos/](https://bekary.velohoster.com/pos/)
- **New Production Batch (নতুন ব্যাচ তৈরি):** [https://bekary.velohoster.com/inventory/production/create/](https://bekary.velohoster.com/inventory/production/create/)
- **Production Batches List (সকল ব্যাচ):** [https://bekary.velohoster.com/inventory/production/](https://bekary.velohoster.com/inventory/production/)
- **Production Reports (উৎপাদন ও খরচ রিপোর্ট):** [https://bekary.velohoster.com/inventory/production/reports/](https://bekary.velohoster.com/inventory/production/reports/)
- **New Hawker Challan (নতুন চালান তৈরি):** [https://bekary.velohoster.com/pos/hawkers/dispatch/](https://bekary.velohoster.com/pos/hawkers/dispatch/)
- **Hawker Distribution List (সকল চালান):** [https://bekary.velohoster.com/pos/hawkers/](https://bekary.velohoster.com/pos/hawkers/)
- **Hawker Due Reports (হকার বকেয়া রিপোর্ট):** [https://bekary.velohoster.com/pos/hawkers/reports/](https://bekary.velohoster.com/pos/hawkers/reports/)
- **Unfold Admin Console:** [https://bekary.velohoster.com/admin/](https://bekary.velohoster.com/admin/)








খাতার হিসাব	সফটওয়্যারের কোন অপশনে এন্ট্রি হবে
হকার চালান (ছবি ১)	➔ Hawker Delivery (হকার চালান) মেনু থেকে হকার নির্বাচন করে পণ্যের পিস ও রেট দিলেই অটো মোট বিল, জমা ও বকেয়া হয়ে যাবে এবং রসিদ প্রিন্ট হবে।
দৈনিক খরচ ও কাঁচামাল (ছবি ২ ও ৩-এর বাম পাশ)	➔ Inventory (কাঁচামাল ক্রয়) এবং Finance (আয়-ব্যয়) মেনুতে ভাউচার এন্ট্রি হবে।
স্টাফদের বেতন/খোরাকি (ছবি ২ ও ৩-এর নিচে)	➔ Payroll (কর্মী ও বেতন) মেনুতে স্টাফদের নাম ও দৈনিক পেমেন্ট হিসেবে জমা হবে।
কারখানার রুটি/কেক তৈরি (ছবি ৪)	➔ Production (উৎপাদন ও রেসিপি) মেনুতে কোন কাঁচামাল কতটুকু লেগেছে ও কত পিস কেক/রুটি হয়েছে তা এন্ট্রি দিলে স্বয়ংক্রিয়ভাবে স্টক আপডেট হবে।
দিনশেষের লাল কালির ক্যাশ হিসাব	➔ Dashboard এবং General Ledger (খতিয়ান)-এ স্বয়ংক্রিয়ভাবে মোট বিক্রয়, মোট খরচ বাদ দিয়ে আজকের নেট ক্যাশ কত তা ভেসে উঠবে।