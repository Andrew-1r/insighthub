# dashboardapp/urls.py
from django.urls import path
from . import views

from .views import (
    DashboardUpdateView,
    DashboardDeleteView,
    UserCSVUpdateView,
    UserCSVDeleteView,
    generate_qr_code,
    dashboard_list,
    dashboard_create,
    csv_list,
    csv_upload,
    dashboard_detail,
    get_chart_data,
    chatui,
)

urlpatterns = [
    path('', views.index, name='home'),

    # Dashboards
    path('dashboards/', dashboard_list, name='dashboard_list'),
    path('dashboards/create/', dashboard_create, name='dashboard_create'),
    path('dashboard/<int:pk>/edit/', DashboardUpdateView.as_view(), name='dashboard_edit'),
    path('dashboard/<int:pk>/delete/', DashboardDeleteView.as_view(), name='dashboard_delete'),
    path('dashboard/<int:user_pk>/<int:dashboard_pk>/', dashboard_detail, name='dashboard_detail'),
    path('dashboards/<int:pk>/update/', DashboardUpdateView.as_view(), name='dashboard_update'),
    path('dashboard/<int:user_pk>/<int:dashboard_pk>/save_layout/', views.save_dashboard_layout, name='save_dashboard_layout'),
    path('api/get_chart_data/', views.get_chart_data, name='get_chart_data'),

    # CSVs
    path('csvs/', csv_list, name='csv_list'),
    path('csvs/upload/', csv_upload, name='csv_upload'),
    path('csv/<int:pk>/edit/', UserCSVUpdateView.as_view(), name='csv_edit'),
    path('csv/<int:pk>/delete/', UserCSVDeleteView.as_view(), name='csv_delete'),

    # QR code & sharing
    path('dashboard/<int:dashboard_id>/generate_qr/', generate_qr_code, name='generate_qr'),

    # OpenAI chatbot integration
    path("chatui", views.chatui, name="chatui"),
    path("chatbot/", views.chatbot, name="chatbot"),
]