# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/users/", include("namito.users.urls")),
    path("api/accounts/", include("allauth.urls")),
    path("api/carts/", include("namito.orders.urls")),
    path("api/", include("namito.pages.urls")),
    path('api/', include("namito.catalog.urls")),
    path('api/', include("namito.advertisement.urls")),

    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
schema_view = get_schema_view(
    openapi.Info(
        title="Namito API",
        default_version="v1",
        description="API documentation for Namito",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)
# API URLS
urlpatterns += [
    # API base url
    path("/", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("api/", include("config.api_router")),
    # DRF auth token
    # path("auth-token/", obtain_auth_token),
    path("", include("namito.openapi.urls")),
    path("", TemplateView.as_view(template_name="catalog/index.html")),
    #                re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.api.views.handle_not_found'

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
