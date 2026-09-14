import time
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Bỏ qua các URL đăng nhập, đăng xuất, đăng ký
            exempt_paths = ['/accounts/login/', '/accounts/register/', '/accounts/logout/']
            if request.path in exempt_paths:
                return self.get_response(request)

            current_time = time.time()
            if 'last_activity' not in request.session:
                request.session['last_activity'] = current_time

            last_activity = request.session.get('last_activity', current_time)
            timeout = getattr(settings, 'SESSION_COOKIE_AGE', 86400)

            # Chỉ kiểm tra timeout khi session đã hoạt động ít nhất 5 giây
            if current_time - last_activity > timeout and current_time - last_activity > 5:
                logout(request)
                messages.error(request, "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.")
                return redirect('login')

            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response