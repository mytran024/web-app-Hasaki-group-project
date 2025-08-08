import calendar
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime as dt, timedelta, date
from .models import Customer, Appointment, Service, Employee, Feedback, WorkShifts, Messenger
from .helpers import get_appointment, read_data
from .enums import AppointmentStatusType, DeletedType, FeedbackStatusType, PriorityType

tables = {
    'CUSTOMER': 'Customers',
    'SERVICE': 'Services',
    'EMPLOYEE': 'Employees',
    'APPOINTMENT': 'Appointments',
    'FEEDBACK': 'Feedback',
    'WORK_SHIFT': 'WorkShifts',
    'MESSENGER': 'Messengers'
}


def home(request):
    if request.method == "GET":
        for key, value in tables.items():
            if (value == tables['CUSTOMER'] and Customer.objects.all().values().count() > 0) or \
                    (value == tables['SERVICE'] and Service.objects.all().values().count() > 0) or \
                    (value == tables['APPOINTMENT'] and Appointment.objects.all().values().count() > 0) or \
                    (value == tables['EMPLOYEE'] and Employee.objects.all().values().count() > 0) or \
                    (value == tables['FEEDBACK'] and Feedback.objects.all().values().count() > 0) or \
                    (value == tables['WORK_SHIFT'] and WorkShifts.objects.all().values().count() > 0) or \
                    (value == tables['MESSENGER'] and Messenger.objects.all().values().count() > 0):
                continue

            lst_data = read_data(value)
            for data in lst_data:
                if value == tables['CUSTOMER']:
                    if not Customer.objects.filter(customer_id=data['customer_id']):
                        customer = Customer(customer_id=data['customer_id'],
                                            customer_name=data['customer_name'],
                                            phone_number=data['phone_number'],
                                            email=data['email'],
                                            created_date=data['created_date'],
                                            is_delete=data['is_delete'])
                        customer.save()
                elif value == tables['SERVICE']:
                    if not Service.objects.filter(service_id=data['service_id']):
                        service = Service(service_id=data['service_id'],
                                          service_name=data['service_name'],
                                          description=data['description'])
                        service.save()
                elif value == tables['EMPLOYEE']:
                    if not Employee.objects.filter(employee_id=data['employee_id']):
                        employee = Employee(employee_id=data['employee_id'],
                                            employee_name=data['employee_name'],
                                            email=data['email'],
                                            phone_number=data['phone_number'],
                                            password=data['password'],
                                            created_date=data['created_date'])
                        employee.save()
                elif value == tables['APPOINTMENT']:
                    if not Appointment.objects.filter(appointment_id=data['appointment_id']):
                        appointment = Appointment(appointment_id=data['appointment_id'],
                                                  customer_id=data['customer_id'],
                                                  service_id=data['service_id'],
                                                  employee_id=data['employee_id'],
                                                  appointment_date=dt.strptime(data['appointment_date'],
                                                                               "%d/%m/%Y").date(),
                                                  start_time=data['start_time'],
                                                  end_time=data['end_time'],
                                                  status=data['status'],
                                                  note=data['note'],
                                                  is_delete=data['is_delete'])
                        appointment.save()
                elif value == tables['FEEDBACK']:
                    if not Feedback.objects.filter(request_id=data['request_id']):
                        feedback = Feedback(request_id=data['request_id'],
                                            customer_id=data['customer_id'],
                                            employee_id=data['employee_id'],
                                            service_id=data['service_id'],
                                            status=data['status'],
                                            prioritize=data['prioritize'],
                                            request_content=data['request_content'],
                                            request_date=data['request_date'],
                                            is_delete=data['is_delete'])
                        feedback.save()
                elif value == tables['WORK_SHIFT']:
                    if not WorkShifts.objects.filter(shifts_id=data['shifts_id']):
                        workShifts = WorkShifts(shifts_id=data['shifts_id'],
                                                employee_id=data['employee_id'],
                                                shifts_date=data['shifts_date'],
                                                shifts_detail=data['shifts_detail'],
                                                is_delete=data['is_delete'])
                        workShifts.save()
                elif value == tables['MESSENGER']:
                    if not Messenger.objects.filter(messenger_id=data['messenger_id']):
                        messenger = Messenger(messenger_id=data['messenger_id'],
                                              customer_id=data['customer_id'],
                                              employee_id=data['employee_id'],
                                              message=data['message'],
                                              is_sent_from_customer=data['is_sent_from_customer'],
                                              sent_time=data['sent_time'],
                                              is_resolved=data['is_resolved'],
                                              is_delete=data['is_delete'])
                        messenger.save()
        return render(request, '../templates/home.html')


@csrf_protect
def login(request):
    if request.method == 'GET':
        return render(request, '../templates/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username or not password:
        messages.error(request, 'Vui lòng kiểm tra lại tài khoản đăng nhập!')
        return redirect(request.path)

    employees = Employee.objects.filter(Q(email=username) | Q(phone_number=username)).values()

    for employee in employees:
        if employee['password'] == password:
            request.session['employee_id'] = employee['employee_id']
            messages.success(request, "Đăng nhập thành công!")
            return redirect("/schedules")

    messages.error(request, 'Tài khoản không tồn tại!')
    return redirect(request.path)


@csrf_protect
def appointment_booking(request):
    services = Service.objects.all()
    if request.method == "GET":
        context = {
            'isSuccess': False,
            'services': services
        }
        return render(request, '../templates/appointment_booking.html', {'context': context})

    # Check validity of fields on form
    customer_name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    note = request.POST.get('note')
    service = request.POST.get('service')
    appointment_date = request.POST.get('appointment_date')
    start_time = request.POST.get('start_time')
    service_time = request.POST.get('service_time')
    end_time = None

    if (customer_name == '') or (phone == '') or (email == '') or (int(service) == -1) or \
            (appointment_date == '') or (start_time == ''):
        messages.error(request, 'Vui lòng điền đủ thông tin!')
        context = {
            'isSuccess': False,
            'services': services
        }
        return render(request, '../templates/appointment_booking.html', {'context': context})

    booking_time = dt.strptime(start_time, '%H:%M').time()
    range_time = None
    if booking_time.hour >= 9 and booking_time.hour < 13:
        range_time = "Sáng (9h - 13h00)"
    elif booking_time.hour >= 13 and booking_time.hour < 17:
        range_time = "Chiều (13h00 - 17h00)"
    else:
        range_time = "Tối (17h00 - 20h00)"

    available_employees = WorkShifts.objects.filter(shifts_date=appointment_date).filter(
        shifts_detail__contains=range_time).values()
    if available_employees.count() == 0:
        messages.error(request, "Hiện tại không có nhân viên cho khung giờ này! Vui lòng chọn khung giờ khác!")
        return redirect(request.path)

    if available_employees.count() == 5:
        messages.error(request, "Hiện tại đã full nhân viên cho khung giờ này! Vui lòng chọn khung giờ khác!")
        return redirect(request.path)

    customer = Customer.objects.filter(phone_number=phone).first()
    new_customer = None
    if not customer:
        new_customer = Customer(
            customer_name=customer_name,
            phone_number=phone,
            email=email
        )
        new_customer.save()

    service_obj = Service.objects.filter(service_id=service).first()
    minutes = (float(service_time) * 60) if service_time else 30
    end_time = (dt.strptime(str(start_time), "%H:%M") + timedelta(minutes=minutes)).time()
    employee_id = available_employees.first()['employee_id']
    employee = Employee.objects.get(employee_id=employee_id)

    appointment = Appointment(
        customer=customer if customer else new_customer,
        service=service_obj,
        employee=employee,
        appointment_date=appointment_date,
        start_time=dt.strptime(str(start_time), "%H:%M").time(),
        end_time=end_time,
        status=AppointmentStatusType.INCOMPLETE.value,
        note=note
    )
    appointment.save()

    context = {
        'isSuccess': True,
        'customer_name': customer_name,
        'phone': phone,
        'email': email,
        'service': service_obj.service_name if service_obj else "Không dịch vụ",
        'appointment_date': appointment_date,
        'note': note,
        'start_time': start_time,
        'end_time': f"{str(end_time.hour).zfill(2)}:{str(end_time.minute).zfill(2)}",
        'start_clock_type': "AM" if int(str(start_time).split(":")[0]) < 12 else "PM",
        'end_clock_type': "AM" if end_time.hour < 12 else "PM"
    }
    return render(request, '../templates/appointment_booking.html', {'context': context})


@csrf_protect
def support(request):
    services = Service.objects.all().values()

    if request.method == 'GET':
        context = {
            'isShowModal': False,
            'services': services
        }
        return render(request, '../templates/request.html', {'context': context})

    customer_name = request.POST.get('customer_name')
    phone_number = request.POST.get('phone_number')
    email = request.POST.get('email')
    service = request.POST.get('service')
    content = request.POST.get('request_content')

    try:
        customer = Customer.objects.get(phone_number=phone_number)
        new_customer = None
        if not customer:
            new_customer = Customer(
                customer_name=customer_name,
                phone_number=phone_number,
                email=email
            )
            new_customer.save()

        feedback = Feedback(
            customer=customer if customer else new_customer,
            service=Service.objects.get(service_id=service),
            request_content=content
        )
        feedback.save()

        context = {
            'customer': customer_name,
            'phone': phone_number,
            'service': Service.objects.get(service_id=service),
            'content': content,
            'request_date': feedback.request_date,
            'isShowModal': True,
            'services': services
        }
    except Exception as e:
        context = {
            'customer': customer_name,
            'phone': phone_number,
            'service': Service.objects.get(service_id=service),
            'content': content,
            'isShowModal': False,
            'services': services
        }
    return render(request, '../templates/request.html', {'context': context})


@csrf_protect
def register_work_shifts(request):
    employee_id = request.session.get('employee_id')
    employee = Employee.objects.get(employee_id=employee_id)

    if request.method == 'GET':
        if not employee_id:
            return redirect('/login')
        context = {
            'isSuccess': False,
            'employee': employee,
            'default_date': dt.today().strftime('%Y-%m-%d')
        }
        return render(request, '../templates/register_work_shifts.html', {'context': context})

    shifts_date = request.POST.get('shifts_date')
    shifts_detail = request.POST.get('shifts_detail')

    if dt.strptime(shifts_date, '%Y-%m-%d').date() < dt.today().date():
        messages.error(request, 'Ngày đăng ký không hợp lệ!')
        context = {
            'isSuccess': False,
            'employee': employee,
            'default_date': dt.strptime(shifts_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        }
        return render(request, '../templates/register_work_shifts.html', {'context': context})

    if int(shifts_detail) < 0:
        messages.error(request, 'Vui lòng chọn ca làm việc!')
        return redirect(request.META.get('HTTP_REFERER'))

    detail = None
    if int(shifts_detail) == 0:
        detail = "Sáng (9h - 13h00)"
    elif int(shifts_detail) == 1:
        detail = "Chiều (13h00 - 17h00)"
    else:
        detail = "Tối (17h00 - 20h00)"

    work_shift = WorkShifts.objects.filter(
        employee_id=employee_id,
        shifts_date=dt.strptime(shifts_date, '%Y-%m-%d').date()
    ).values().first()

    if work_shift:
        details = [detail for detail in work_shift['shifts_detail'].split(';')]
        if detail in details:
            messages.error(request, 'Vui lòng chọn ca làm khác!')
            return redirect(request.path)

        WorkShifts.objects.filter(
            employee_id=employee_id,
            shifts_date=dt.strptime(shifts_date, '%Y-%m-%d').date()
        ).update(shifts_detail=work_shift['shifts_detail'] + ';' + detail)
    else:
        work_shift = WorkShifts(
            employee=employee,
            shifts_date=dt.strptime(shifts_date, '%Y-%m-%d').date(),
            shifts_detail=detail
        )
        work_shift.save()

    context = {
        'isSuccess': True,
        'employee': employee,
        'default_date': dt.today().strftime('%Y-%m-%d'),
        'info': {
            'employee_name': employee.employee_name,
            'phone_number': employee.phone_number,
            'shifts_date': dt.strptime(shifts_date, '%Y-%m-%d').date(),
            'shifts_detail': detail
        }
    }
    return render(request, '../templates/register_work_shifts.html', {'context': context})


def work_shifts(request):
    if request.method == 'GET':
        if not request.session.get('employee_id'):
            return redirect('/login')

        month = int(request.GET.get('month')) if request.GET.get('month') else dt.today().month
        year = int(request.GET.get('year')) if request.GET.get('year') else dt.today().year
        week = int(request.GET.get('week')) if request.GET.get('week') else 1
        employee_id = request.session.get('employee_id')

        if not employee_id:
            messages.error(request, 'Vui lòng đăng nhập để xem thông tin!')
            return redirect(request.path)

        if not month or not year:
            month = dt.today().month
            year = dt.today().year

        cal = calendar.monthcalendar(year, month)
        week_days = cal[week - 1]
        dates_of_week = []
        for i, day in enumerate(week_days):
            if day != 0:
                dates_of_week.append(date(year, month, day))

        morning = "Sáng (9h - 13h00)"
        afternoon = "Chiều (13h00 - 17h00)"
        evening = "Tối (17h00 - 20h00)"
        data = []
        for day in dates_of_week:
            work_shift = WorkShifts.objects.filter(
                employee_id=employee_id,
                shifts_date=day
            ).first()
            info = dict()
            if work_shift:
                details = [detail for detail in work_shift.shifts_detail.split(';')]
                info = {
                    'day': day,
                    'is_morning': True if morning in details else False,
                    'is_afternoon': True if afternoon in details else False,
                    'is_evening': True if evening in details else False
                }
            else:
                info = {
                    'day': day,
                    'is_morning': False,
                    'is_afternoon': False,
                    'is_evening': False
                }
            data.append(info)

        context = {
            'current_date': dt.today().strftime('%Y-%m'),
            'week_days': dates_of_week,
            'week_number': week,
            'weeks': [i for i in range(1, len(cal) + 1)],
            'data': data,
            'employee': Employee.objects.get(employee_id=employee_id)
        }
        return render(request, '../templates/personal_work_shifts.html', {'context': context})


@csrf_protect
def phone_verify(request):
    if request.method == 'POST':
        return redirect('/reset-password')
    return render(request, '../templates/phone_verification.html')


def logout(request):
    request.session.pop('employee_id', None)
    return redirect('/')


@csrf_protect
def reset_password(request):
    if request.method == 'GET':
        return render(request, '../templates/new_password.html')
    return redirect('/')


def schedules(request):
    if request.method == 'GET':
        if not request.session.get('employee_id'):
            return redirect('/login')

        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')

        today = dt.today()

        # Convert to integers (with defaults for current year, month, and day)
        year = int(year) if year else today.year
        month = int(month) if month else today.month
        day = int(day) if day else today.day
        appointments = get_appointment(year=year, month=month, day=day)

        employee_id = request.session.get('employee_id')
        employee = None
        if employee_id:
            employee = Employee.objects.get(employee_id=int(employee_id))

        data = dict()

        for key in appointments.keys():
            data[key] = []
            for item in appointments[key]:
                info = {
                    'appointment': item['appointment_info'],
                    'customer': Customer.objects.get(customer_id=item['appointment_info']['customer_id']),
                    'employee': Employee.objects.get(employee_id=item['appointment_info']['employee_id']),
                    'service': Service.objects.get(service_id=item['appointment_info']['service_id'])
                }
                data[key].append(info)

        context = {
            'data': data,
            'filterDate': date(year, month, day).strftime('%Y-%m-%d'),
            'employee': employee
        }
        return render(request, '../templates/appointments.html', {"context": context})


def customers(request):
    if request.method == 'GET':
        if not request.session.get('employee_id'):
            return redirect('/login')

        customers = Customer.objects.filter(is_delete=DeletedType.AVAILABLE.value).values().order_by('customer_id')
        paginator = Paginator(customers, 12)
        page_number = request.GET.get('page')
        if not page_number:
            page_number = 1

        employee_id = request.session.get('employee_id')
        employee = None
        if employee_id:
            employee = Employee.objects.get(employee_id=int(employee_id))

        customers_per_page = paginator.get_page(page_number)
        context = {
            'customers': customers_per_page,
            'employee': employee
        }
        return render(request, '../templates/customers.html', {'context': context})


def cancel_appointment(request, appointment_id):
    if request.method == 'POST':
        previous_url = request.META.get('HTTP_REFERER')
        appointment = Appointment.objects.get(appointment_id=appointment_id)

        if appointment:
            appointment.status = AppointmentStatusType.CANCEL.value
            appointment.save()
            return redirect(previous_url)


def detail_customer(request, customer_id):
    if request.method == 'GET':
        if not request.session.get('employee_id'):
            return redirect('/login')

        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')

        today = dt.today()
        year = int(year) if year else today.year
        month = int(month) if month else today.month
        day = int(day) if day else today.day

        customer = Customer.objects.get(customer_id=id)
        appointments = Appointment.objects.filter(customer_id=customer_id) \
            .filter(appointment_date=date(year=year, month=month, day=day)).values()

        employee_id = request.session.get('employee_id')
        employee = None
        if employee_id:
            employee = Employee.objects.get(employee_id=int(employee_id))

        context = {
            'customer': customer,
            'appointments': appointments,
            'filterDate': date(year=year, month=month, day=day).strftime('%Y-%m-%d'),
            'employee': employee
        }
        return render(request, '../templates/customer_detail_info.html', {'context': context})


def delete_customer(request, customer_id):
    if request.method == 'POST':
        customer = Customer.objects.get(customer_id=customer_id)
        if customer:
            appointments = Appointment.objects.filter(customer_id=customer.customer_id)
            if appointments:
                appointments.update(is_delete=DeletedType.DELETED.value)

            customer.is_delete = DeletedType.DELETED.value
            customer.save()
            return redirect("/customers")


@csrf_protect
def edit_customer(request, customer_id):
    if request.method == 'POST':
        customer = Customer.objects.get(customer_id=customer_id)
        if customer:
            customer.customer_name = request.POST.get('customer_name')
            customer.email = request.POST.get('email')
            customer.phone_number = request.POST.get('phone_number')
            customer.save()
            return redirect('/customers/detail/{0}'.format(id))


def messenger(request):
    if request.method == 'GET':
        if not request.session.get('employee_id'):
            return redirect('/login')

        customer_id = request.GET.get('customer_id')
        customers = Messenger.objects.values('customer_id').distinct()
        data = []

        for customer in customers:
            messages = Messenger.objects.filter(customer_id=customer['customer_id']).values('message').order_by(
                '-sent_time')
            info = {
                'customer': Customer.objects.get(customer_id=customer['customer_id']),
                'messages': messages
            }
            data.append(info)

        detailData = None
        if customer_id:
            for dta in data:
                if dta['customer'].customer_id == int(customer_id):
                    detailData = dta
                    break
        else:
            detailData = data[0]

        chatTemplate = render_to_string('../templates/messenger_content.html', {'context': detailData}, request)

        context = {
            'data': data,
            'chatTemplate': chatTemplate
        }

        return render(request, '../templates/messenger.html', {'context': context})


def feedbacks(request):
    employee_id = request.session.get('employee_id')
    if request.method == 'GET':
        if not employee_id:
            return redirect('/login')

        employee = Employee.objects.get(employee_id=employee_id)
        feedbacks = Feedback.objects.all().values()
        info = []

        for feedback in feedbacks:
            customer = Customer.objects.filter(customer_id=feedback['customer_id']).values().first()
            service = Service.objects.filter(service_id=feedback['service_id']).values().first()
            data = {
                'feedback': feedback,
                'customer': customer,
                'service': service,
            }
            info.append(data)

        context = {
            'employee': employee,
            'info': info,
        }
        return render(request, '../templates/feedback.html', {'context': context})


def feedback_detail(request, feedback_id):
    employee_id = request.session.get('employee_id')
    if request.method == 'GET':
        if not employee_id:
            return redirect('/login')

    if request.method == 'GET':
        feedback = Feedback.objects.get(request_id=feedback_id)
        employee = Employee.objects.get(employee_id=employee_id)
        customer = Customer.objects.get(customer_id=feedback.customer_id)
        service = Service.objects.get(service_id=feedback.service_id)

        context = {
            'feedback': feedback,
            'customer': customer,
            'employee': employee,
            'service': service,
        }
        return render(request, '../templates/feedback_detail.html', {'context': context})