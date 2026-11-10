from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from config.htmx_utils import render_htmx
from .forms import SiteSettingForm
from .models import SiteSetting


@login_required(login_url='/login/')
def site_settings_view(request):
    setting, _ = SiteSetting.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = SiteSettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            success_msg = "Bakery settings updated successfully!"
            if getattr(request, 'htmx', False):
                fresh_form = SiteSettingForm(instance=setting)
                logo_html = render_to_string('partials/sidebar_logo.html', request=request)
                logo_oob = f'<div hx-swap-oob="outerHTML:#sidebar-logo">{logo_html}</div>'
                return render_htmx(
                    request,
                    'pages/settings.html',
                    {'form': fresh_form},
                    toast_success=success_msg,
                    extra_oob=[logo_oob],
                )

            messages.success(request, success_msg)
            return redirect('site_settings')
        else:
            if getattr(request, 'htmx', False):
                return render_htmx(
                    request,
                    'pages/settings.html',
                    {'form': form},
                    form_errors=form.errors,
                )
    else:
        form = SiteSettingForm(instance=setting)

    return render(request, 'pages/settings.html', {'form': form})
