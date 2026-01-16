from django.urls import path
from .views import AddressListView, AddressDetailView, AddressSetDefaultView

app_name = 'address'

urlpatterns = [
    path('', AddressListView.as_view(), name='address-list'),
    path('<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('<int:pk>/set-default/', AddressSetDefaultView.as_view(), name='address-set-default'),
]
