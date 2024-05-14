from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView
from django.conf.urls.i18n import i18n_patterns
# from django_telethon.urls import django_telethon_urls
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# from rest_framework.authtoken.views import obtain_auth_token

if settings.MAIN_CONTAINER:
    from config import startup_code

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/blank.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/blank.html"), name="about"
    ),
    # path(settings.ADMIN_URL, admin.site.urls),
    path("tgbot/", include("tgbot.urls", namespace="tgbot")),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicons/favicon.ico', permanent=True)),
    # path('telegram/', django_telethon_urls()),
    # User management
    # path("users/", include("library_tgbot.users.urls", namespace="users")),
    # path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("api/" + settings.ADMIN_URL, admin.site.urls),
    prefix_default_language=False
)
# API URLS
# urlpatterns += [
#     # API base url
#     path("api/", include("config.api_router")),
#     # DRF auth token
#     path("auth-token/", obtain_auth_token),
#     path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
#     path(
#         "api/docs/",
#         SpectacularSwaggerView.as_view(url_name="api-schema"),
#         name="api-docs",
#     ),
# ]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
