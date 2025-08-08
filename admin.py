from django.contrib import admin
from .models import Customer, Employee, Appointment, Service, Feedback, WorkShifts, Messenger

# Register your models here.
admin.register(Customer)
admin.register(Employee)
admin.register(Appointment)
admin.register(WorkShifts)
admin.register(Messenger)
admin.register(Service)
admin.register(Feedback)