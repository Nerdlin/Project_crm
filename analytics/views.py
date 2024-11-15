from django.shortcuts import render
from django.db.models import Count
from crm.models import TelegramUser
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import base64
import csv
from django.http import HttpResponse
from collections import Counter
import json


from django.shortcuts import render
def analytics_home(request):
    return render(request, 'analytics/base.html')


def gender_distribution(request):
    return render(request, 'analytics/gender_distribution.html')
                  
# Helper function to convert matplotlib plots to base64 for embedding in HTML
def render_chart_to_base64(plt):
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return image_base64

# 1. Gender Distribution with Percentages
def gender_distribution(request):
    gender_data = TelegramUser.objects.values('gender').annotate(total=Count('gender'))
    total_count = sum(item['total'] for item in gender_data)
    for item in gender_data:
        item['percentage'] = (item['total'] / total_count) * 100
    return render(request, 'analytics/gender_distribution.html', {'gender_data': gender_data})


# 2. Age Category Distribution with Percentages
def age_category_distribution(request):
    users = TelegramUser.objects.all().values('age')
    df = pd.DataFrame(users)

    bins = [18, 25, 35, 50, 100]
    labels = ['18-25', '26-35', '36-50', '50+']
    df['age_category'] = pd.cut(df['age'], bins=bins, labels=labels)

    age_category_counts = df['age_category'].value_counts().sort_index()
    total_count = age_category_counts.sum()
    age_category_percentages = (age_category_counts / total_count) * 100

    plt.figure(figsize=(8, 4))
    sns.barplot(x=age_category_percentages.index, y=age_category_percentages.values, palette="viridis")
    plt.title('Age Category Distribution (Percentage)')
    plt.xlabel('Age Category')
    plt.ylabel('Percentage (%)')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/age_category_distribution.html', {'chart': chart})


# 3. Region Distribution with Percentages
def region_distribution(request):
    region_data = TelegramUser.objects.values('region').annotate(total=Count('region'))
    total_count = sum(item['total'] for item in region_data)
    for item in region_data:
        item['percentage'] = (item['total'] / total_count) * 100
    return render(request, 'analytics/region_distribution.html', {'region_data': region_data})


# 4. Benefits Distribution with Percentages in Pie Chart
def benefits_distribution(request):
    users = TelegramUser.objects.all().values('benefits')
    df = pd.DataFrame(users)

    benefits_data = {
        'receiving_benefits': df['benefits'].sum(),
        'not_receiving_benefits': len(df) - df['benefits'].sum()
    }

    total_count = benefits_data['receiving_benefits'] + benefits_data['not_receiving_benefits']
    percentages = [
        (benefits_data['receiving_benefits'] / total_count) * 100,
        (benefits_data['not_receiving_benefits'] / total_count) * 100
    ]

    plt.figure(figsize=(6, 6))
    plt.pie(
        [benefits_data['receiving_benefits'], benefits_data['not_receiving_benefits']],
        labels=['Receiving Benefits', 'Not Receiving Benefits'],
        autopct='%1.1f%%',
        startangle=140,
        colors=['#66c2a5', '#fc8d62']
    )
    plt.title('Benefits Distribution')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/benefits_distribution.html', {'chart': chart})


def average_children_by_age_group(request):
    users = TelegramUser.objects.all().values('age', 'children')
    df = pd.DataFrame(users)

    bins = [18, 25, 35, 50, 100]
    labels = ['18-25', '26-35', '36-50', '50+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels)

    avg_children = df.groupby('age_group')['children'].mean()
    std_dev_children = df.groupby('age_group')['children'].apply(np.std)

    plt.figure(figsize=(8, 4))
    sns.barplot(x=avg_children.index, y=avg_children.values, yerr=std_dev_children, palette="coolwarm")
    plt.title('Average Number of Children by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Average Children')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/average_children_by_age_group.html', {'chart': chart})



# выгрузки данных в формат PDF или CSV
def export_gender_distribution_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gender_distribution.csv"'

    writer = csv.writer(response)
    writer.writerow(['Gender', 'Total', 'Percentage'])

    gender_data = TelegramUser.objects.values('gender').annotate(total=Count('gender'))
    total_count = sum(item['total'] for item in gender_data)
    for item in gender_data:
        percentage = (item['total'] / total_count) * 100
        writer.writerow([item['gender'], item['total'], f"{percentage:.2f}%"])

    return response




# 1. Анализ активности пользователей по времени
def user_activity_over_time(request):
    users = TelegramUser.objects.values('last_activity')
    df = pd.DataFrame(users)
    df['last_activity'] = pd.to_datetime(df['last_activity'])
    df['day_of_week'] = df['last_activity'].dt.day_name()  # Получаем день недели
    activity_counts = df['day_of_week'].value_counts().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(x=activity_counts.index, y=activity_counts.values, palette="coolwarm")
    plt.title('User Activity by Day of Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Activities')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/user_activity_over_time.html', {'chart': chart})

def function_usage_analysis(request):
    users = TelegramUser.objects.values_list('used_functions', flat=True)
    function_usage = Counter()
    for used_functions in users:
        if used_functions:  # Проверяем, что поле не пустое
            function_usage.update(json.loads(used_functions))

    function_names = list(function_usage.keys())
    usage_counts = list(function_usage.values())

    plt.figure(figsize=(12, 6))
    sns.barplot(x=function_names, y=usage_counts, color='skyblue')
    plt.title('Function Usage Analysis')
    plt.xlabel('Function')
    plt.ylabel('Usage Count')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/function_usage_analysis.html', {'chart': chart})



# 3. Анализ среднего балла за квизы
def quiz_points_distribution(request):
    users = TelegramUser.objects.values('quiz_points')
    df = pd.DataFrame(users)
    df['quiz_points'] = pd.to_numeric(df['quiz_points'],
                                      errors='coerce')  # Преобразуем в числовой формат, игнорируя ошибки
    quiz_points_distribution = df['quiz_points'].dropna()  # Убираем пустые значения

    plt.figure(figsize=(10, 6))
    sns.histplot(quiz_points_distribution, kde=True, color='purple', bins=10)
    plt.title('Quiz Points Distribution')
    plt.xlabel('Quiz Points')
    plt.ylabel('Frequency')

    chart = render_chart_to_base64(plt)
    plt.close()

    return render(request, 'analytics/quiz_points_distribution.html', {'chart': chart})
