from django.urls import path, re_path, include, reverse_lazy
from . import views, views_account, views_syllabus, views_actions
from django.contrib.auth import views as auth_views
from .views_classbased.syllabus import SyllabusView

#
urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views_account.logout_request, name='logout'),
    path('login/', views_account.login_request, name='login'),
    re_path(r'^profile/(?:(?P<username>[\w\d]+)/)?$', views_account.profile, name='profile'),
    path('user_update/', views_account.user_update, name='user_update'),
    path('membership_update/', views_account.membership_update, name='membership_update'),
    path('register/', views_account.register, name='register'),
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

    path('register_confirm/<name>/<id>', views_account.register_confirm, name='register_confirm'),
    path('forgot_password/', views_account.forgot_password, name='forgot_password'),
    path('user_home/', views.home, name='user_home'),

    re_path(r'^syllabus/(?:filter-(?P<filter>[\w ,/%\d]+)/)?(?:whose-(?P<whose>[\w\d,]*)/)?$', SyllabusView.as_view(), name='syllabus'),

    path('add_exercise/', views_actions.do_add_exercise, name='add_exercise'),
    path('add_exercises/', views_actions.do_add_exercises, name='add_exercises'),
    path('add_exercise_group/', views_actions.do_add_exercise_group, name='add_exercise_group'),
    path('edit_exercises/', views_actions.do_edit_exercises, name='edit_exercises'),
    path('rate/', views_actions.do_rate, name='rate'),
    path('edit_exercises_groups/', views_actions.do_edit_exercises_groups, name='edit_exercises_groups'),
    path('do_edit_session/', views_actions.do_edit_session, name='do_edit_session'),
    path('do_send_session_emails/<session_id>', views_actions.do_send_session_emails, name='do_send_session_emails'),

    path('restart/', views_account.restart, name='restart'),

    path('exercise_editing/', views_syllabus.exercise_editing, name='exercise_editing'),
    path('sessions/', views_syllabus.sessions, name='sessions'),
    path('view_session/<id>', views_syllabus.view_session, name='view_session'),
    re_path(r'^edit_session/(?:(?P<id>\d+)/)?$', views_syllabus.edit_session, name='edit_session'),
]   