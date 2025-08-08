from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('home', views.home, name='home'),
    path('booking', views.appointment_booking, name='booking'),
    path('forgot-password/phone-verify', views.phone_verify, name='phone-verify'),
    path('reset-password', views.reset_password, name='reset-password'),
    path('schedules', views.schedules, name='schedules'),
    path('cancel-appointment/<int:appointment_id>', views.cancel_appointment, name='cancel-appointment'),
    path('customers', views.customers, name='customers'),
    path('customers/detail/<int:customer_id>', views.detail_customer, name='detail-customer'),
    path('customers/delete/<int:customer_id>', views.delete_customer, name='delete-customer'),
    path('customers/edit/<int:id>', views.edit_customer, name='edit-customer'),
    path('messenger', views.messenger, name='messenger'),
    path('support', views.support, name='support'),
    path('register-work-shifts', views.register_work_shifts, name='register-work_shifts'),
    path('work-shifts', views.work_shifts, name='work-shifts'),
    path('list-feedback', views.feedbacks, name='list-feedback'),
    path('feedback/<int:feedback_id>', views.feedback_detail, name='feedback-detail'),
]