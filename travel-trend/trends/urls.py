from django.urls import path
from .views import TrendsView, RouteView

urlpatterns = [
    path('trends/', TrendsView.as_view(), name='trends'),
    path('route/', RouteView.as_view(), name='route'),
]
