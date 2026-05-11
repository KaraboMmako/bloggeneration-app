from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView
from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("forgot-password/", views.forgot_password_page, name="forgot_password"),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="frontend/password_reset_confirm.html",
            success_url=reverse_lazy("frontend:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="frontend/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("logout/", views.logout_page, name="logout"),
    path(
        "password/change/",
        PasswordChangeView.as_view(
            template_name="frontend/change_password.html",
            success_url=reverse_lazy("frontend:dashboard"),
        ),
        name="change_password",
    ),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("blogs/create/", views.generate_blog_page, name="generate_blog"),
    path("blogs/<int:pk>/", views.blog_detail_page, name="blog_detail"),
    path("sections/<int:section_id>/regenerate/",views.regenerate_section_page,name="regenerate_section"),
    path("sections/<int:section_id>/update/", views.update_section_page, name="update_section"),
    path("sections/<int:section_id>/generate-image/",views.generate_section_image_page,name="generate_section_image",),
    path("blogs/<int:pk>/delete/", views.delete_blog_page, name="delete_blog"),
    path("blogs/<int:pk>/regenerate/", views.regenerate_blog_page, name="regenerate_blog"),
    path("blogs/<int:pk>/publish/", views.publish_blog_page, name="publish_blog"),
    path("blogs/<int:pk>/set-status/", views.set_blog_status_page, name="set_blog_status"),
]