# Django + HTMX + Alpine.js + Tailwind CSS v4 Boilerplate Architecture & Standards

Welcome to your production-grade, high-performance web boilerplate! Below are senior architectural guidelines and design system standards to maintain maximum speed, testability, and scalability.

---

## ⚡ 1. Performance & Caching Strategy

### Low-Level Caching for Global Context
- **Global Context Processors** (like `site_settings`) utilize **Django Low-Level Caching (`cache.get / cache.set`)** with `post_save` signal invalidation.
- **Rule**: Never run raw, un-cached database queries inside a global `context_processor`. Always wrap global data in a cache block to keep per-request DB queries at **0**.

### Production Static Asset Compression
- For production deployments, use **WhiteNoise** with `CompressedManifestStaticFilesStorage` (configured in `settings.py`) for cache-busting hashed static filenames.

---

## 🚀 2. HTMX Single-Template Architecture (No `_full.html` Duplication)

### Dynamic Base Template Pattern
Each dashboard view requires only **one single template file**:
```html
<!-- templates/pages/feature.html -->
{% extends base_template %}

{% block content %}
<div class="w-full max-w-full space-y-8 p-4 sm:p-6 lg:p-8">
    <!-- Feature content -->
</div>
{% endblock %}
```

In `views.py`, standard rendering handles both full reloads and HTMX partial swaps automatically:
```python
@login_required(login_url='/login/')
def feature_view(request):
    return render(request, 'pages/feature.html', context)
```
- When accessed directly: `base_template` resolves to `'base.html'`.
- When navigated via HTMX (`hx-boost` or `hx-get`): `base_template` resolves to `'base_partial.html'`.

### HTMX Forms & File Uploads
- When submitting forms via HTMX that include file/image fields, always include:
  ```html
  <form action="{% url 'route_name' %}" method="POST" hx-post="{% url 'route_name' %}" hx-target="#main-content" hx-encoding="multipart/form-data">
  ```

### Out-Of-Band (OOB) Toasts & Targeted Swaps
- Use `render_htmx` from `config.htmx_utils`:
  ```python
  from config.htmx_utils import render_htmx

  return render_htmx(
      request,
      'pages/feature.html',
      {'form': form},
      toast_success="সফলভাবে সংরক্ষণ করা হয়েছে!",
      extra_oob=['<div hx-swap-oob="outerHTML:#sidebar-logo">...</div>']
  )
  ```
- Or use standard Django `messages.success(request, '...')` — the built-in `HtmxMessagesMiddleware` automatically transforms messages into Out-Of-Band toast swaps for HTMX requests!

---

## 🎨 3. Tailwind CSS v4 CSS-First Configuration

### Clean Asset Pipeline
- **Source Location**: `assets/css/input.css` (kept strictly outside `STATICFILES_DIRS` to avoid `collectstatic` conflicts).
- **Output Target**: `static/css/style.css` (collected and hashed by WhiteNoise).
- **Targeted File Scanning (`@source`)**:
  ```css
  @import "tailwindcss";
  @source "../../templates";
  @source "../../apps";
  ```

---

## 🧪 4. Automated Testing Suite (`test.py`)

- Run tests at any time using:
  ```bash
  python3 test.py
  # or
  python3 manage.py test
  # or
  make test
  ```
- Tests validate:
  1. Health check `/health/`
  2. Dynamic base template behavior (full vs partial HTMX)
  3. Authentication flows (standard 302 and `HX-Redirect`)
  4. Site settings persistence and OOB toast rendering
  5. Configuration integrity

---

## 📁 5. Directory Structure Overview

```
mysocial/
├── assets/
│   └── css/input.css      # Pure Tailwind CSS v4 source file (outside static)
├── apps/
│   ├── accounts/          # Custom User model, authentication & dashboard views
│   └── site_settings/     # Branding, logos, favicons & context processor
├── config/
│   ├── settings.py        # 12-factor settings driven by .env
│   ├── context_processors.py # Dynamic base_template selector
│   ├── htmx_utils.py      # HTMX render helpers & message middleware
│   └── views.py           # Health check endpoint
├── static/
│   ├── css/style.css      # Compiled production stylesheet
│   └── images/            # Static assets
├── templates/
│   ├── base.html          # Main SPA shell (progress bar, modal container, CSRF handler)
│   ├── base_partial.html  # Minimal content wrapper for HTMX requests
│   ├── components/        # Reusable DHAT components (modal, confirm dialog, search)
│   ├── pages/             # Single-file dashboard page templates
│   └── partials/          # Header, sidebar, toast notification partials
├── .env.example           # Environment variables template
├── Makefile               # Developer workflow shortcuts
├── test.py                # Automated test suite
└── DEVELOPMENT_GUIDANCE.md
```



Email Address	admin@bakemaster.com
Phone Number (বিকল্প)	01700000000
Password	admin12345
User Role	Super Admin (Full System Access)