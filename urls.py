from django.urls import path, include, reverse_lazy
from . import views, account_views, add_data_views
from django.contrib.auth import views as auth_views
from .class_views.syllabus import SyllabusView

#
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', account_views.logout_request, name='logout'),
    path('login/', account_views.login_request, name='login'),
    path('profile/', account_views.profile, name='profile'),
    path('register/', account_views.register, name='register'),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(template_name='SyllabusTrackerApp/change-password.html'),
        name="password_change"
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='SyllabusTrackerApp/change-password-done.html'),
        name="password_change_done"
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='SyllabusTrackerApp/reset-password-done.html'),
        name="password_reset_done"
    ),
    path(
        'password_reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='SyllabusTrackerApp/reset-password-confirm.html'),
        name="password_reset_confirm"
    ),
    path(
        'password_reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='SyllabusTrackerApp/reset-password-complete.html'),
        name="password_reset_complete"
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='SyllabusTrackerApp/reset-password.html'),
        name="password_reset"
    ),

    path('register_confirm/<name>/<id>', account_views.register_confirm, name='register_confirm'),
    path('forgot_password/', account_views.forgot_password, name='forgot_password'),
    path('user_home/', views.home, name='user_home'),
    path('syllabus/', SyllabusView.as_view(), name='syllabus'),
    path('syllabus/<whose>/', SyllabusView.as_view(), name='syllabus_summary'),
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