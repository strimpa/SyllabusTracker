from django.urls import path, include
from . import views, account_views, add_data_views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', account_views.logout_request, name='logout'),
    path('login/', account_views.login_request, name='login'),
    path('profile/', account_views.profile, name='profile'),
    path('register/', account_views.register, name='register'),
    path('forgot_password/', account_views.forgot_password, name='forgot_password'),
    path('user_home/', views.home, name='user_home'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('add_exercise/', add_data_views.add_exercise, name='add_exercise'),
    path('add_exercises/', add_data_views.add_exercises, name='add_exercises'),
    path('add_exercise_group/', add_data_views.add_exercise_group, name='add_exercise_group'),
    path('edit_exercises/', add_data_views.edit_exercises, name='edit_exercises'),
    path('rate/', add_data_views.rate, name='rate'),
    path('edit_exercises_groups/', add_data_views.edit_exercises_groups, name='edit_exercises_groups'),
    path('exercise_editing/', views.exercise_editing, name='exercise_editing'),
    path('add_kyus/', views.add_kyus, name='add_kyus'),

#    path('accounts/', include('django.contrib.auth.urls')),
]   