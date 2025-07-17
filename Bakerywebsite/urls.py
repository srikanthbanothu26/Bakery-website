"""
URL configuration for Bakerywebsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from Home.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('Home.urls')),
                  path('store/', include('Store.urls')),
                  path('user/', include('userauth.urls')),
                  path('pos/', include('pointofsale.urls')),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

                  # Serve robots.txt from static folder
                  re_path(r'^robots\.txt$', serve, {
                      'document_root': settings.STATICFILES_DIRS[0],  # Serve from static folder
                      'path': 'robots.txt',
                  }),
              ] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
