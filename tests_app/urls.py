from django.urls import path
from . import views, api_views

app_name = 'tests_app'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Question Management
    path('questions/', views.question_list, name='question_list'),
    path('questions/add/', views.question_add, name='question_add'),
    path('questions/<int:pk>/', views.question_detail, name='question_detail'),
    path('questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),
    path('questions/<int:pk>/duplicate/', views.question_duplicate, name='question_duplicate'),
    
    # CSV Export
    path('export/question/<int:pk>/', views.export_question_csv, name='export_question_csv'),
    path('export/test/', views.export_test_csv, name='export_test_csv'),
    
    # AJAX Endpoints
    path('ajax/load-domains/', views.ajax_load_domains, name='ajax_load_domains'),
    
    # API Endpoints (for external apps like Chrome extension)
    path('api/questions/create/', api_views.api_create_question, name='api_create_question'),
    path('api/exams/', api_views.api_get_exams_and_domains, name='api_get_exams'),
    path('api/stats/', api_views.api_get_question_stats, name='api_get_stats'),
]