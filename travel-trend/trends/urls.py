from django.urls import path
from .views import TrendsView, RouteView, CategoryRankingView, TravelTrendStaticView

urlpatterns = [
    path('trends/', TrendsView.as_view(), name='trends'),
    path('trends/categories/', CategoryRankingView.as_view(), name='category-rankings'),
    path('route/', RouteView.as_view(), name='route'),
    path('trends/data/', TravelTrendStaticView.as_view(), name='travel-trend-data'),
]
