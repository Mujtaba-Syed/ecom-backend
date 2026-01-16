from django.urls import path
from .views import CategoryListView, CategoryDetailView

app_name = 'category'

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]
