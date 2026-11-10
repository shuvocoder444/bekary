# Workspace Development Rules & Design System Guidelines

All code changes and new feature development in this codebase MUST follow the standard operating procedures documented in [`DEVELOPMENT_GUIDANCE.md`](file:///Users/sawon/My/htmx%20boilerplate/dms/DEVELOPMENT_GUIDANCE.md).

## Core Rules Summary

1. **CRUD Forms**:
   - Always include `action="{% url 'route_name' %}" method="POST"` and `hx-post="{% url 'route_name' %}" hx-target="#main-content"` on forms.
   - Always include `hx-encoding="multipart/form-data"` on forms with file/image inputs.
   - Use `FileField` for SVG/ICO uploads.

2. **Toast Notifications**:
   - ALWAYS use `templates/partials/toast.html` positioned at `fixed top-20 right-6 z-99999` (Top-Right, below header navbar).
   - In HTMX views, return `toast.html` using Out-Of-Band (OOB) swap.

3. **Sidebar Navigation & Active State**:
   - Active route MUST be initialized with `x-data="{ selected: '{{ request.resolver_match.url_name|default:'dashboard' }}' }"`.
   - On branding updates, swap ONLY `<a id="sidebar-logo">` with `hx-swap-oob="outerHTML:#sidebar-logo"`. Do NOT swap `<aside id="sidebar">`.

4. **Layout & Dark Mode**:
   - Dashboard pages must be full width (`w-full max-w-full p-4 sm:p-6 lg:p-8`).
   - File upload text must use `.file-upload-wrapper` to ensure high contrast in dark mode (`dark:text-gray-300`).
