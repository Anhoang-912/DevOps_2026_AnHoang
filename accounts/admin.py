from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashWidget, ReadOnlyPasswordHashField,
    UserChangeForm as BaseUserChangeForm,
    UserCreationForm as BaseUserCreationForm
)
from django.utils.html import mark_safe
from store.models import Profile, Order


class CustomReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    template_name = "auth/widgets/read_only_password_hash.html"

    def render(self, name, value, attrs=None, renderer=None):
        from django.template.loader import render_to_string
        context = self.get_context(name, value, attrs)
        return mark_safe(render_to_string(self.template_name, context))


class CustomUserChangeForm(BaseUserChangeForm):
    password = ReadOnlyPasswordHashField(
        label="Mật khẩu bảo mật",
        widget=CustomReadOnlyPasswordHashWidget,
        help_text="Mật khẩu được mã hóa an toàn bằng thuật toán một chiều. Bấm nút đặt lại mật khẩu để thay đổi."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].label = "Tên đăng nhập"
            self.fields['username'].help_text = "Tối đa 150 ký tự. Cho phép chữ cái, chữ số và các ký tự: @ . + - _"
        if 'first_name' in self.fields:
            self.fields['first_name'].label = "Tên"
        if 'last_name' in self.fields:
            self.fields['last_name'].label = "Họ & Tên đệm"
        if 'email' in self.fields:
            self.fields['email'].label = "Địa chỉ email"
        if 'is_active' in self.fields:
            self.fields['is_active'].label = "Kích hoạt tài khoản"
            self.fields['is_active'].help_text = "Cho phép người dùng đăng nhập hệ thống"
        if 'is_staff' in self.fields:
            self.fields['is_staff'].label = "Quyền nhân viên (Admin)"
            self.fields['is_staff'].help_text = "Cho phép truy cập trang quản trị hệ thống"
        if 'is_superuser' in self.fields:
            self.fields['is_superuser'].label = "Siêu quản trị viên"
            self.fields['is_superuser'].help_text = "Có toàn bộ quyền hạn cao nhất"
        if 'groups' in self.fields:
            self.fields['groups'].label = "Nhóm quyền người dùng"
        if 'user_permissions' in self.fields:
            self.fields['user_permissions'].label = "Quyền hạn chi tiết"
        if 'last_login' in self.fields:
            self.fields['last_login'].label = "Đăng nhập lần cuối"
        if 'date_joined' in self.fields:
            self.fields['date_joined'].label = "Ngày đăng ký tài khoản"


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Hồ sơ người dùng (Profile)'
    fk_name = 'user'
    fields = ['avatar_preview', 'avatar', 'plain_password', ('phone_number', 'birthdate'), 'address', 'bio', 'facebook']
    readonly_fields = ['avatar_preview']

    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" style="width: 68px; height: 68px; border-radius: 50%; object-fit: cover; border: 2.5px solid #4f46e5; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);" />')
        return "Chưa có ảnh đại diện"
    avatar_preview.short_description = "Ảnh đại diện hiện tại"


class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    inlines = (ProfileInline,)
    list_display = ('username', 'plain_password_display', 'full_name_display', 'email', 'phone_display', 'order_count', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone_number')

    fieldsets = (
        ('1. Tài khoản & Bảo mật', {
            'fields': ('username', 'password')
        }),
        ('2. Thông tin cá nhân', {
            'fields': (('last_name', 'first_name'), 'email')
        }),
        ('3. Phân quyền & Vai trò', {
            'fields': (('is_active', 'is_staff', 'is_superuser'), 'groups', 'user_permissions')
        }),
        ('4. Lịch sử hoạt động', {
            'fields': (('last_login', 'date_joined'),)
        }),
    )

    def plain_password_display(self, obj):
        try:
            pwd = obj.profile.plain_password
            if pwd:
                return mark_safe(f'<code style="background:#e0e7ff; color:#3730a3; padding:3px 8px; border-radius:6px; font-weight:700; font-size:12px; letter-spacing:0.5px;">{pwd}</code>')
            return mark_safe('<span style="color:#94a3b8; font-style:italic;">Chưa lưu</span>')
        except Profile.DoesNotExist:
            return "—"
    plain_password_display.short_description = "Mật khẩu (Xem)"

    def full_name_display(self, obj):
        name = obj.get_full_name()
        return name if name else "—"
    full_name_display.short_description = "Họ và tên"
    
    def phone_display(self, obj):
        try:
            return obj.profile.phone_number or "—"
        except Profile.DoesNotExist:
            return "—"
    phone_display.short_description = "Số điện thoại"

    def order_count(self, obj):
        count = Order.objects.filter(user=obj).count()
        if count > 0:
            return mark_safe(f'<a href="/admin/store/order/?user__id__exact={obj.id}" class="admin-badge badge-processing">{count} đơn</a>')
        return "0 đơn"
    order_count.short_description = "Đơn hàng"


# Hủy đăng ký User mặc định và đăng ký UserAdmin mới
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['avatar_thumb', 'user', 'plain_password_display', 'phone_number', 'address', 'birthdate']
    search_fields = ['user__username', 'user__email', 'phone_number', 'address', 'plain_password']
    fields = ['user', 'avatar', 'plain_password', 'phone_number', 'address', 'bio', 'birthdate', 'facebook', 'twitter', 'instagram']

    def avatar_thumb(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" class="admin-thumb" style="border-radius: 50%; width: 40px; height: 40px; object-fit: cover;" />')
        return mark_safe('<div style="width:40px; height:40px; border-radius:50%; background:#e2e8f0; display:flex; align-items:center; justify-content:center; font-size:12px;">👤</div>')
    avatar_thumb.short_description = "Avatar"

    def plain_password_display(self, obj):
        if obj.plain_password:
            return mark_safe(f'<code style="background:#e0e7ff; color:#3730a3; padding:3px 8px; border-radius:6px; font-weight:700; font-size:12px;">{obj.plain_password}</code>')
        return "—"
    plain_password_display.short_description = "Mật khẩu (Xem)"
