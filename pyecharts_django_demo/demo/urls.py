from django.urls import path
from . import views

urlpatterns = [
    path(r'line/<str:FigType>/', views.ChartView.as_view(), name='demo'),
    path(r'lineUpdate/', views.ChartUpdateView.as_view(), name='demo'),
    path(r'index/', views.IndexView.as_view(), name='demo'),
]
