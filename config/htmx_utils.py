from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


def htmx_redirect(url: str) -> HttpResponse:
    """Returns an HTTP response instructing HTMX to redirect to the specified URL."""
    response = HttpResponse()
    response['HX-Redirect'] = url
    return response


def render_htmx(request, template_name: str, context: dict = None, toast_success: str = None, 
                toast_error: str = None, form_errors=None, extra_oob: list = None):
    """
    Renders an HTMX response with support for Out-Of-Band (OOB) toasts and targeted DOM swaps.
    Strictly uses templates/partials/toast.html adhering to the workspace rules.
    """
    context = context or {}
    if toast_success:
        context['success'] = toast_success
    if toast_error:
        context['error'] = toast_error
    if form_errors:
        context['form_errors'] = form_errors

    response = render(request, template_name, context)

    if getattr(request, 'htmx', False):
        oob_items = []
        if extra_oob:
            if isinstance(extra_oob, (list, tuple)):
                oob_items.extend(extra_oob)
            else:
                oob_items.append(extra_oob)

        # Render toast partial if any notification payload exists
        if toast_success or toast_error or form_errors:
            toast_html = render_to_string('partials/toast.html', context, request=request)
            oob_items.append(toast_html)

        if oob_items:
            response.content += "".join(oob_items).encode('utf-8')

    return response


class HtmxMessagesMiddleware:
    """
    Middleware that automatically appends Django messages as an Out-Of-Band (OOB)
    swap of templates/partials/toast.html for HTMX requests.
    Enables views to simply use messages.success(request, '...') for both HTMX and non-HTMX.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process HTMX requests that are standard HTML responses and not redirects
        if getattr(request, 'htmx', False) and response.status_code == 200:
            content_type = response.get('Content-Type', '')
            if 'text/html' in content_type and not response.has_header('HX-Redirect'):
                from django.contrib.messages import get_messages
                messages = get_messages(request)
                if messages:
                    toast_html = render_to_string('partials/toast.html', {'messages': messages}, request=request)
                    response.content += toast_html.encode('utf-8')

        return response
