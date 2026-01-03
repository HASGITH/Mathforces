# archive/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('contests/', views.contest_list, name='contest_list'),
    path('contests/<int:pk>/', views.contest_dashboard, name='contest_dashboard'),
    path('contests/<int:pk>/standings/', views.contest_standings, name='contest_standings'),
    
    # Это главная строка: теперь URL может быть /problem/1/ или /contest/2/problem/1/
    path('problem/<int:pk>/', views.problem_detail, name='problem_detail'),
    path('contests/<int:contest_id>/problem/<int:pk>/', views.problem_detail, name='contest_problem_detail'),

    path('contest/<int:pk>/calculate/', views.calculate_contest_rating, name='calculate_rating'),

    path('profile/', views.profile_view, name='profile_view'), # Добавь это
    path('user/<str:username>/', views.user_profile_view, name='user_profile'),

    path('search/', views.user_search, name='user_search'),
    path('user/<str:username>/toggle-friend/', views.toggle_friend, name='toggle_friend'),
    path('friends/', views.friends_list_view, name='friends_list'),

    path('ranking/', views.ranking_view, name='ranking'),
    path('submission/<int:pk>/manual/<str:action>/', views.manual_update_submission, name='manual_update_submission'),
]