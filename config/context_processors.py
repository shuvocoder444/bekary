def base_template(request):
    """
    DHAT Dynamic Template Strategy:
    Returns 'base_partial.html' when the request is sent via HTMX (or hx-boost),
    and 'base.html' when loaded directly or reloaded in the browser.
    Eliminates the need for duplicate *_full.html templates.
    """
    is_htmx = getattr(request, 'htmx', False)
    return {
        'base_template': 'base_partial.html' if is_htmx else 'base.html',
        'is_htmx': bool(is_htmx),
    }
