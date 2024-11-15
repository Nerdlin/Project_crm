from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты аналитики
    path('', views.analytics_home, name='analytics_home'),
    path('gender/', views.gender_distribution, name='gender_distribution'),
    path('age_category/', views.age_category_distribution, name='age_category_distribution'),
    path('region/', views.region_distribution, name='region_distribution'),
    path('benefits/', views.benefits_distribution, name='benefits_distribution'),
    path('average_children_by_age_group/', views.average_children_by_age_group, name='average_children_by_age_group'),

    # Дополнительные маршруты аналитики
    path('user_activity_over_time/', views.user_activity_over_time, name='user_activity_over_time'),
    path('function_usage/', views.function_usage_analysis, name='function_usage_analysis'),
    path('quiz_points_distribution/', views.quiz_points_distribution, name='quiz_points_distribution'),

    # Маршрут для экспорта данных в CSV
    path('export_gender_distribution_csv/', views.export_gender_distribution_csv,
         name='export_gender_distribution_csv'),
]
