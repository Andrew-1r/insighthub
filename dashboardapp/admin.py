# admin.py

from django.contrib import admin
from .models import (
    UserProfile, UserCSV, CSVHeading,
    CSVValue, Dashboard
)

# TODO: adjust list_display and search_fields as appropriate

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(UserCSV)
class UserCSVAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'csv_title', 'uploaded_at', 'csv_file']
    search_fields = ['csv_title', 'user__user__username']


@admin.register(CSVHeading)
class CSVHeadingAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv', 'heading_name']
    search_fields = ['heading_name', 'csv__csv_title']


@admin.register(CSVValue)
class CSVValueAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv', 'heading', 'row_index', 'value']
    search_fields = ['value', 'heading__heading_name']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_public', 'qr_code_image', 'created_at', 'layout_json']
    search_fields = ['title', 'user__user__username']
