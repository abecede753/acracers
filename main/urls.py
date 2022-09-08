from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


from main import views

urlpatterns = [
    #    url(r'frontpage', include('noc.apps.frontpage.urls',
    #        namespace='frontpage', app_name='frontpage')),

    path('', views.Home.as_view(), name="home"),
    # TODO cache needs some big thinking...
    # vary_on_cookie isnt enough. we also need to empty cache when any
    # change happens in upcoming or current.
    # path('home_update/',
    #      vary_on_cookie(cache_page(5)(views.HomeUpdate.as_view())),
    #      name="home_update"),
    path('home_update/', views.HomeUpdate.as_view(), name="home_update"),
    path('steamlogin/', views.steamlogin, name="steamlogin"),
    path('steamlogin/callback/', views.steamlogin_callback),
    path('profile/<int:pk>/', views.PropsUpdateView.as_view(), name="profile"),

    path('aadmin/', admin.site.urls),
    path('adhoc/', include('adhoc.urls', namespace="adhoc")),
] + \
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
