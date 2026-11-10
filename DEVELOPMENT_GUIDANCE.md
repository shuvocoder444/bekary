# 📘 Modern Web App Architecture & CRUD Standard Operating Procedures (SOP)

Welcome to the official developer guidance document for this boilerplate. This document establishes **mandatory rules, architectural patterns, and troubleshooting guidelines** for creating new CRUD operations, maintaining design consistency, and preventing common runtime errors.

---

## 🚀 1. CRUD Form & Route Standards (Preventing 404 / 500 Errors)

Whenever building or modifying any CRUD feature (Create, Read, Update, Delete):

### A. Form Action & HTMX Attributes Rule
Every `<form>` MUST have both HTML fallback and HTMX SPA attributes:
```html
<form 
    action="{% url 'item_create' %}"
    method="POST"
    hx-post="{% url 'item_create' %}" 
    hx-target="#main-content" 
    hx-encoding="multipart/form-data" 
    class="space-y-6"
>
    {% csrf_token %}
    ...
</form>
```
* **Why**: Explicit `action` prevents 404 URL resolution bugs when HTMX falls back or when browsers execute standard form submission.
* **Multipart Encoding**: Always include `hx-encoding="multipart/form-data"` if the form has any file/image inputs (`FileField`, `ImageField`).

### B. Django 5 `STORAGES` Configuration Rule
In `config/settings.py`, Django 5 requires both `'default'` and `'staticfiles'` in `STORAGES`:
```python
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```
* **Critical**: Omitting `'default'` causes Django file upload handlers to crash with a `500 Internal Server Error (InvalidStorageError)`.

### C. SVG & Favicon FileField Rule
* Use `models.FileField` instead of `models.ImageField` for branding fields (logos, icons, favicons) to allow `.svg`, `.ico`, `.png`, `.jpg`, and `.webp` uploads without Pillow validation crashes.

---

## 🍞 2. Universal Toast Notification System (Single Source of Truth)

All notifications (Success, Error, Warning, Info) across the entire application MUST follow this centralized pattern:

### A. Central Component Location
All toast markup resides in **[`templates/partials/toast.html`](file:///Users/sawon/My/htmx%20boilerplate/dms/templates/partials/toast.html)**.
* **Fixed Position**: `fixed top-20 right-6 z-99999` (Top-Right, directly below the header navbar, right of notification icons).
* **Auto-Dismiss**: Managed via Alpine.js (`x-data="{ show: true }" x-init="setTimeout(() => show = false, 3500)"`).

### B. View-Level HTMX OOB Toast Trigger Pattern
In Django views, trigger toasts on HTMX responses using `render_htmx` or standard Django `messages`:

**Option 1: Using `render_htmx` (Recommended for custom OOB payloads like logos):**
```python
from config.htmx_utils import render_htmx

# Inside HTMX POST view handler:
if request.htmx:
    return render_htmx(
        request, 
        'pages/item_detail.html', 
        {'form': fresh_form},
        toast_success="সফলভাবে সংরক্ষণ করা হয়েছে!",
        extra_oob=['<div hx-swap-oob="outerHTML:#sidebar-logo">...</div>']
    )
```

**Option 2: Using standard Django Messages (`messages.success`):**
```python
from django.contrib import messages

# Messages are automatically converted to OOB toast swaps on HTMX requests by HtmxMessagesMiddleware!
messages.success(request, "সফলভাবে সংরক্ষণ করা হয়েছে!")
return render(request, 'pages/item_detail.html', {'form': fresh_form})
```
* On standard page redirects, `messages.success(...)` is rendered automatically on full page loads via `templates/base.html`.
* On HTMX SPA requests, `HtmxMessagesMiddleware` automatically renders `templates/partials/toast.html` as an Out-Of-Band (OOB) swap.

---

## 📌 3. Sidebar Active State & Zero-Flicker Branding Updates

### A. URL Resolver Active Route Persistence
In [`templates/partials/sidebar.html`](file:///Users/sawon/My/htmx%20boilerplate/dms/templates/partials/sidebar.html), initialize navigation state using Django's resolver match:
```html
<nav x-data="{ selected: '{{ request.resolver_match.url_name|default:'dashboard' }}' }">
```
* **Why**: This guarantees that when a user reloads or refreshes the browser on ANY page (e.g. `/dashboard/calendar/`), the active highlight stays strictly on that page.

### B. Targeted Out-Of-Band (OOB) Logo Swap Rule
When updating site settings or branding via HTMX:
* **Rule**: Swap ONLY `<a id="sidebar-logo">` using `hx-swap-oob="outerHTML:#sidebar-logo"`.
* **NEVER** replace the entire `<aside id="sidebar">` container during HTMX swaps. Swapping `<aside>` causes full DOM node re-insertion, triggering layout reflow and visual sidebar flickering.

---

## 🎨 4. Responsive UI & Dark Mode Text Guidelines

### A. Full-Width Container Standard
Main page templates in `templates/pages/*.html` MUST use full-width responsive padding:
```html
<div class="w-full max-w-full space-y-8 p-4 sm:p-6 lg:p-8">
    ...
</div>
```

### B. File Upload Input Dark Mode Contrast Rule
Wrap file inputs in `.file-upload-wrapper` to ensure Django's plain text widgets (`Currently:`, `Clear`, `Change:`) remain bright and readable (`text-gray-600 dark:text-gray-300`) in dark mode.

---

## 🛠️ Quick Checklist for New Features

- [ ] Route named cleanly in `urls.py`
- [ ] View implements HTMX + Full Page dual rendering
- [ ] Form has `action`, `method="POST"`, `hx-post`, and `hx-encoding="multipart/form-data"` (if file inputs exist)
- [ ] Success/Error triggers centralized `partials/toast.html`
- [ ] Sidebar link added with `@click="selected = 'route_name'"`
- [ ] Main page wrapped in `w-full max-w-full p-4 sm:p-6 lg:p-8`
