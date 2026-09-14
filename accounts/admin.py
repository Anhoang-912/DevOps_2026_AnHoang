from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from store.models import Profile, Order

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Hồ sơ người dùng (Profile)'
    fk_name = 'user'
    fields = ['avatar_preview', 'avatar', 'plain_password', 'phone_number', 'address', 'bio', 'birthdate', 'facebook']
    readonly_fields = ['avatar_preview']

    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #4f46e5;" />')
        return "Chưa có ảnh đại diện"
    avatar_preview.short_description = "Ảnh đại diện"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'plain_password_display', 'full_name_display', 'email', 'phone_display', 'order_count', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone_number')

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
            return mark_safe(f'<img src="{obj.avatar.url}" class="admin-thumb" style="border-radius: 50%; width: 40px; height: 40px;" />')
        return mark_safe('<div style="width:40px; height:40px; border-radius:50%; background:#e2e8f0; display:flex; align-items:center; justify-content:center; font-size:12px;">👤</div>')
    avatar_thumb.short_description = "Avatar"

    def plain_password_display(self, obj):
        if obj.plain_password:
            return mark_safe(f'<code style="background:#e0e7ff; color:#3730a3; padding:3px 8px; border-radius:6px; font-weight:700; font-size:12px;">{obj.plain_password}</code>')
        return "—"
    plain_password_display.short_description = "Mật khẩu (Xem)"
