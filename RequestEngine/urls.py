"""
URL configuration for RequestEngine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from Portal.deploy_views import DeployWebhookView
from Portal.frontend_views import serve_frontend
from Portal.views import (
    AuthLoginView,
    AuthRefreshView,
    ChangePasswordView,
    CurrentUserView,
    LogoutView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("Portal.urls")),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("api/auth/token/refresh/", AuthRefreshView.as_view(), name="auth-refresh"),
    path("api/auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path(
        "api/auth/change-password/",
        ChangePasswordView.as_view(),
        name="auth-change-password",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/deploy-webhook/", DeployWebhookView.as_view(), name="deploy-webhook"),
]
urlpatterns += [
    re_path(r"^(?!admin(?:/|$)|api(?:/|$)|static(?:/|$))(?P<path>.*)$", serve_frontend),
]
