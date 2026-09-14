from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from store.models import Profile
from django import forms
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
import time

# Form Profile mở rộng
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=False)

    class Meta:
        model = Profile
        fields = [
            'avatar', 'bio', 'phone_number', 'address', 'birthdate',
            'website', 'facebook', 'twitter', 'instagram'
        ]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

# View đăng ký
@csrf_protect
@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1', '') or request.POST.get('password', '')
        password_confirm = request.POST.get('password2', '') or request.POST.get('password_confirm', '')

        errors = []

        if not username:
            errors.append('Vui lòng nhập tên đăng nhập.')
        elif User.objects.filter(username=username).exists():
            errors.append(f'Tên đăng nhập "{username}" đã tồn tại. Vui lòng chọn tên khác.')

        if not password:
            errors.append('Vui lòng nhập mật khẩu.')
        elif len(password) < 6:
            errors.append('Mật khẩu phải có ít nhất 6 ký tự.')

        if password != password_confirm:
            errors.append('Mật khẩu xác nhận không trùng khớp.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'initial_data': {
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            })

        try:
            # Tạo tài khoản người dùng
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Lưu plain_password vào Profile để admin có thể xem
            try:
                profile = user.profile
                profile.plain_password = password
                profile.save()
            except Profile.DoesNotExist:
                Profile.objects.create(user=user, plain_password=password)

            # Tự động đăng nhập ngay sau khi đăng ký thành công
            login(request, user)
            messages.success(request, f'Chào mừng {user.username}! Bạn đã đăng ký và đăng nhập thành công.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra khi tạo tài khoản: {str(e)}')
            return render(request, 'accounts/register.html')
    else:
        return render(request, 'accounts/register.html')

# View đăng nhập (bảo vệ CSRF và chống cache token cũ)
@sensitive_post_parameters('password')
@csrf_protect
@never_cache
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Nếu user trước đó đang đăng nhập (ví dụ admin), logout an toàn để chuyển phiên
            if request.user.is_authenticated:
                logout(request)

            # Đăng nhập với user mới
            user = form.get_user()
            login(request, user)

            # Khởi tạo thời gian hoạt động
            request.session['last_activity'] = time.time()
            request.session.modified = True

            messages.success(request, f'Chào mừng {user.username}! Bạn đã đăng nhập thành công.')
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại!')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })

# View đăng xuất
@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('home')

# View hồ sơ cá nhân
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Cập nhật User
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Cập nhật Profile
            form.save()

            messages.success(request, 'Thông tin cá nhân đã được cập nhật thành công!')
            return redirect('account_profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(request, 'accounts/profile.html', context)
