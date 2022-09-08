from django.urls import path
from adhoc import views

app_name = "adhoc"
urlpatterns = [
    path('create/', views.AdhocCreateView.as_view(), name="create"),
    path('delete/<int:pk>', views.AdhocDeleteView.as_view(), name="delete"),
    path('kill/', views.AdhocKill.as_view(), name="kill"),
]
