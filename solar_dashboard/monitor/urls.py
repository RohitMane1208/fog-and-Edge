from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/latest/', views.latest_sensor_data, name='latest_sensor_data'),
    path('api/recent/', views.recent_readings, name='recent_readings'),
]