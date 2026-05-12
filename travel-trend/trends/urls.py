from django.urls import path
from .views import TrendsView, RouteView, CategoryRankingView

urlpatterns = [
    path('trends/', TrendsView.as_view(), name='trends'),
    path('trends/categories/', CategoryRankingView.as_view(), name='category-rankings'),
    path('route/', RouteView.as_view(), name='route'),
]
