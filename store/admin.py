from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib import messages
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import (
    Product, Category, CartItem, Order, OrderItem, Review, 
    Profile, Province, District, Ward
)

# Cấu hình branding Django Admin
admin.site.site_header = "Hệ thống Quản trị E-Commerce"
admin.site.site_title = "Quản trị Shop An Hoang"
admin.site.index_title = "Bảng điều khiển quản trị"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_thumbnail', 'product', 'quantity_display', 'price_display', 'subtotal_display']
    fields = ['product_thumbnail', 'product', 'quantity_display', 'price_display', 'subtotal_display']
    can_delete = False
    
    def product_thumbnail(self, obj):
        if obj.product and obj.product.image:
            return mark_safe(f'<img src="{obj.product.image.url}" class="admin-thumb" style="width: 44px; height: 44px; border-radius:6px; object-fit:cover;" />')
        return "—"
    product_thumbnail.short_description = "Ảnh"

    def quantity_display(self, obj):
        return mark_safe(f'<strong style="color:#2563eb; font-size:1rem;">{obj.quantity} cái</strong>')
    quantity_display.short_description = "Số lượng"
    
    def price_display(self, obj):
        return f"{intcomma(obj.price)} VNĐ"
    price_display.short_description = "Đơn giá"
    
    def subtotal_display(self, obj):
        subtotal = obj.price * obj.quantity
        return mark_safe(f"<strong style='color:#dc2626;'>{intcomma(subtotal)} VNĐ</strong>")
    subtotal_display.short_description = "Thành tiền"
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_id_display', 'image_preview', 'product_name_display', 
        'category_badge', 'price_display', 'rating_display', 'actions_column'
    ]
    list_filter = ['category', 'discount_percent']
    search_fields = ['name', 'description']
    list_per_page = 20
    actions = [
        'duplicate_products', 
        'apply_10_percent_discount', 
        'apply_20_percent_discount', 
        'apply_30_percent_discount', 
        'apply_50_percent_discount', 
        'clear_discount'
    ]

    fieldsets = (
        ('1. Thông tin cơ bản', {
            'fields': ('name', 'category', 'description')
        }),
        ('2. Giá cả & Khuyến mãi', {
            'fields': ('price', 'discount_percent')
        }),
        ('3. Hình ảnh sản phẩm', {
            'fields': ('image',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if formfield and hasattr(formfield, 'widget'):
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def product_id_display(self, obj):
        return mark_safe(f'<span style="font-weight:700; color:#64748b; font-size:12.5px;">#{obj.id}</span>')
    product_id_display.short_description = "ID"
    product_id_display.admin_order_field = 'id'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<a href="/admin/store/product/{obj.id}/change/"><img src="{obj.image.url}" class="admin-table-thumb" title="{obj.name}" /></a>')
        return mark_safe('<div class="admin-table-no-thumb"><i class="fas fa-image"></i></div>')
    image_preview.short_description = "Ảnh"

    def product_name_display(self, obj):
        change_url = f"/admin/store/product/{obj.id}/change/"
        desc = ""
        if obj.description:
            clean_desc = obj.description.strip().replace("\n", " ")
            if len(clean_desc) > 55:
                clean_desc = clean_desc[:55] + "..."
            desc = f'<div style="font-size:12px; color:#64748b; margin-top:3px; line-height:1.3;">{clean_desc}</div>'
        return mark_safe(
            f'<div style="display:flex; flex-direction:column;">'
            f'<a href="{change_url}" class="prod-title-link" style="font-weight:700; color:#0f172a; font-size:13.5px; text-decoration:none;">{obj.name}</a>'
            f'{desc}'
            f'</div>'
        )
    product_name_display.short_description = "Tên sản phẩm"
    product_name_display.admin_order_field = 'name'

    def category_badge(self, obj):
        if obj.category:
            cat_url = f"/admin/store/product/?category__id__exact={obj.category.id}"
            return mark_safe(
                f'<a href="{cat_url}" style="text-decoration:none;" title="Xem tất cả sản phẩm trong danh mục {obj.category.name}">'
                f'<span class="cat-pill" style="display:inline-flex; align-items:center; gap:5px; background:#f1f5f9; color:#334155; padding:4px 10px; border-radius:16px; font-weight:600; font-size:12px; border:1px solid #e2e8f0; transition:all 0.15s ease;">'
                f'<i class="fas fa-folder text-primary" style="font-size:11px;"></i> {obj.category.name}'
                f'</span></a>'
            )
        return mark_safe('<span style="color:#94a3b8; font-size:12px; font-style:italic;">Chưa phân loại</span>')
    category_badge.short_description = "Danh mục"
    category_badge.admin_order_field = 'category__name'

    def price_display(self, obj):
        if obj.has_discount:
            return mark_safe(
                f'<div style="line-height:1.35;">'
                f'<div style="color:#ef4444; font-weight:800; font-size:13.5px;">{intcomma(obj.discount_price)} ₫ '
                f'<span style="background:#fee2e2; color:#b91c1c; font-size:11px; font-weight:700; padding:2px 6px; border-radius:6px;">-{obj.discount_percent}%</span></div>'
                f'<div style="color:#94a3b8; font-size:11.5px; text-decoration:line-through; margin-top:2px;">{intcomma(obj.price)} ₫</div>'
                f'</div>'
            )
        return mark_safe(f'<strong style="color:#0f172a; font-size:13.5px;">{intcomma(obj.price)} ₫</strong>')
    price_display.short_description = "Giá bán & Ưu đãi"
    price_display.admin_order_field = 'price'

    def rating_display(self, obj):
        count = obj.rating_count
        if count == 0:
            return mark_safe('<span style="color:#94a3b8; font-size:12px; font-style:italic;">Chưa có</span>')
        stars = round(obj.rating_avg)
        star_str = "★" * stars + "☆" * (5 - stars)
        return mark_safe(f'<span style="color:#f59e0b; font-size:12.5px; letter-spacing:1px;">{star_str}</span> <small style="color:#64748b; font-weight:600;">({count})</small>')
    rating_display.short_description = "Đánh giá"

    def actions_column(self, obj):
        change_url = f"/admin/store/product/{obj.id}/change/"
        delete_url = f"/admin/store/product/{obj.id}/delete/"
        view_url = f"/product/{obj.id}/"
        return mark_safe(
            f'<div style="display:flex; gap:6px; align-items:center;">'
            f'<a href="{view_url}" target="_blank" class="table-action-btn btn-view" title="Xem trên cửa hàng"><i class="fas fa-arrow-up-right-from-square"></i></a>'
            f'<a href="{change_url}" class="table-action-btn btn-edit" title="Chỉnh sửa sản phẩm"><i class="fas fa-pen"></i></a>'
            f'<a href="{delete_url}" class="table-action-btn btn-del" title="Xóa vĩnh viễn sản phẩm" onclick="return confirm(\'Bạn có chắc chắn muốn xóa vĩnh viễn sản phẩm [{obj.name}] khỏi hệ thống không?\');"><i class="fas fa-trash-can"></i></a>'
            f'</div>'
        )
    actions_column.short_description = "Thao tác"

    # Actions thao tác hàng loạt
    @admin.action(description="📋 Nhân bản / Sao chép các sản phẩm đã chọn")
    def duplicate_products(self, request, queryset):
        count = 0
        for product in queryset:
            product.pk = None
            product.id = None
            product.name = f"{product.name} (Bản sao)"
            product.save()
            count += 1
        messages.success(request, f"Đã nhân bản thành công {count} sản phẩm mới.")

    @admin.action(description="⚡ Áp dụng giảm giá 10%% cho các sản phẩm đã chọn")
    def apply_10_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=10)
        messages.success(request, f"Đã áp dụng giảm giá 10% cho {updated} sản phẩm.")

    @admin.action(description="⚡ Áp dụng giảm giá 20%% cho các sản phẩm đã chọn")
    def apply_20_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=20)
        messages.success(request, f"Đã áp dụng giảm giá 20% cho {updated} sản phẩm.")

    @admin.action(description="⚡ Áp dụng giảm giá 30%% cho các sản phẩm đã chọn")
    def apply_30_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=30)
        messages.success(request, f"Đã áp dụng giảm giá 30% cho {updated} sản phẩm.")

    @admin.action(description="⚡ Áp dụng giảm giá 50%% cho các sản phẩm đã chọn")
    def apply_50_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=50)
        messages.success(request, f"Đã áp dụng giảm giá 50% cho {updated} sản phẩm.")

    @admin.action(description="❌ Hủy giảm giá (về 0%%) cho các sản phẩm đã chọn")
    def clear_discount(self, request, queryset):
        updated = queryset.update(discount_percent=0)
        messages.success(request, f"Đã xóa giảm giá cho {updated} sản phẩm.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product_count_link']
    search_fields = ['name']

    def product_count_link(self, obj):
        count = obj.product_set.count()
        return mark_safe(f'<a href="/admin/store/product/?category__id__exact={obj.id}" class="admin-badge badge-processing" title="Xem sản phẩm trong danh mục này">{count} sản phẩm &rarr;</a>')
    product_count_link.short_description = "Sản phẩm"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_info', 'ordered_products_display', 'total_quantity_display',
        'total_display', 'payment_badge', 'status', 'created_at_display', 'actions_column'
    ]
    list_editable = ['status']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['id', 'full_name', 'phone', 'address', 'user__username', 'user__email', 'items__product__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def actions_column(self, obj):
        change_url = f"/admin/store/order/{obj.id}/change/"
        delete_url = f"/admin/store/order/{obj.id}/delete/"
        order_detail_url = f"/order/{obj.id}/"
        return mark_safe(
            f'<div style="display:flex; gap:6px; align-items:center;">'
            f'<a href="{order_detail_url}" class="table-action-btn btn-view" title="Xem chi tiết đơn hàng"><i class="fas fa-receipt"></i></a>'
            f'<a href="{change_url}" class="table-action-btn btn-edit" title="Chỉnh sửa đơn hàng"><i class="fas fa-pen"></i></a>'
            f'<a href="{delete_url}" class="table-action-btn btn-del" title="Xóa đơn hàng này" onclick="return confirm(\'Bạn có chắc chắn muốn xóa đơn hàng #{obj.id} không?\');"><i class="fas fa-trash-can"></i></a>'
            f'</div>'
        )
    actions_column.short_description = "Thao tác"

    fieldsets = (
        ('Trạng thái & Thanh toán', {
            'fields': (('status', 'payment_method'), 'total')
        }),
        ('Thông tin người nhận', {
            'fields': ('user', 'full_name', 'phone', 'address', ('province', 'district', 'ward'), 'note')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items', 'items__product')

    def customer_info(self, obj):
        username = obj.user.username if obj.user else "N/A"
        name = obj.full_name or username
        return mark_safe(f"<strong>{name}</strong><br><small style='color:#64748b;'>{obj.phone} | @{username}</small>")
    customer_info.short_description = "Khách hàng"

    def ordered_products_display(self, obj):
        items = obj.items.all()
        if not items:
            return mark_safe("<span style='color:#94a3b8; font-style:italic;'>Không có sản phẩm</span>")

        lines = []
        for item in items:
            img = ""
            if item.product and item.product.image:
                img = f'<img src="{item.product.image.url}" style="width:30px;height:30px;border-radius:6px;object-fit:cover;margin-right:8px;vertical-align:middle;" />'
            pname = item.product.name if item.product else "Sản phẩm"
            lines.append(
                f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
                f'{img}<span><strong>{pname}</strong> &times; <span style="background:#e0e7ff;color:#3730a3;padding:2px 8px;border-radius:12px;font-weight:700;font-size:11px;">{item.quantity} cái</span></span>'
                f'</div>'
            )
        return mark_safe("".join(lines))
    ordered_products_display.short_description = "Sản phẩm đặt mua"

    def total_quantity_display(self, obj):
        items = list(obj.items.all())
        total_qty = sum(item.quantity for item in items)
        types_count = len(items)
        if types_count <= 1:
            return mark_safe(f'<strong style="color:#2563eb;font-size:14px;">{total_qty} cái</strong>')
        return mark_safe(f'<strong style="color:#2563eb;font-size:14px;">{total_qty} cái</strong><br><small style="color:#64748b;">({types_count} loại SP)</small>')
    total_quantity_display.short_description = "Tổng số lượng"

    def payment_badge(self, obj):
        return mark_safe(f'<span class="admin-badge badge-payment">{obj.get_payment_method_display()}</span>')
    payment_badge.short_description = "Thanh toán"

    def total_display(self, obj):
        return mark_safe(f"<strong style='color:#0f172a;'>{intcomma(obj.total)} VNĐ</strong>")
    total_display.short_description = "Tổng tiền"
    total_display.admin_order_field = 'total'

    def created_at_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
    created_at_display.short_description = "Ngày đặt"
    created_at_display.admin_order_field = 'created_at'

    # Actions cập nhật trạng thái đơn nhanh
    @admin.action(description="✔️ Đánh dấu: ĐÃ XÁC NHẬN")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        messages.success(request, f"Đã chuyển {updated} đơn hàng sang trạng thái 'Đã xác nhận'.")

    @admin.action(description="📦 Đánh dấu: ĐANG XỬ LÝ / ĐÓNG GÓI")
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        messages.success(request, f"Đã chuyển {updated} đơn hàng sang trạng thái 'Đang xử lý'.")

    @admin.action(description="🚚 Đánh dấu: ĐANG GIAO HÀNG")
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        messages.success(request, f"Đã chuyển {updated} đơn hàng sang trạng thái 'Đang giao hàng'.")

    @admin.action(description="✅ Đánh dấu: ĐÃ GIAO THÀNH CÔNG")
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        messages.success(request, f"Đã chuyển {updated} đơn hàng sang trạng thái 'Đã giao hàng'.")

    @admin.action(description="❌ Đánh dấu: HỦY ĐƠN HÀNG")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        messages.warning(request, f"Đã hủy {updated} đơn hàng.")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'order_user', 'product', 'quantity', 'price_display', 'subtotal_display')
    list_filter = ('order__status', 'order__payment_method')
    search_fields = ('order__id', 'product__name', 'order__user__username')
    
    def order_link(self, obj):
        return mark_safe(f'<a href="/admin/store/order/{obj.order.id}/change/">Đơn #{obj.order.id}</a>')
    order_link.short_description = "Đơn hàng"
    
    def order_user(self, obj):
        return obj.order.user.username if obj.order and obj.order.user else "—"
    order_user.short_description = "Khách hàng"
    
    def price_display(self, obj):
        return f"{intcomma(obj.price)} VNĐ"
    price_display.short_description = "Đơn giá"

    def subtotal_display(self, obj):
        return mark_safe(f"<strong>{intcomma(obj.subtotal())} VNĐ</strong>")
    subtotal_display.short_description = "Thành tiền"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating_stars', 'comment_snippet', 'image_thumb', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment', 'product__name', 'user__username']

    def rating_stars(self, obj):
        stars = obj.rating
        star_str = "★" * stars + "☆" * (5 - stars)
        return mark_safe(f'<span class="admin-stars">{star_str}</span> ({stars}/5)')
    rating_stars.short_description = "Số sao"

    def comment_snippet(self, obj):
        if len(obj.comment) > 60:
            return obj.comment[:60] + "..."
        return obj.comment
    comment_snippet.short_description = "Nội dung nhận xét"

    def image_thumb(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="admin-thumb" style="width:40px;height:40px;" />')
        return "—"
    image_thumb.short_description = "Ảnh đính kèm"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_info', 'product_preview', 
        'quantity', 'unit_price_display', 'subtotal_display', 'created_at_display'
    ]
    list_filter = ['created_at', 'product__category']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'product__name']
    list_per_page = 20

    def product_preview(self, obj):
        img_tag = ""
        if obj.product and obj.product.image:
            img_tag = f'<img src="{obj.product.image.url}" class="admin-thumb" style="width:38px;height:38px;border-radius:6px;object-fit:cover;margin-right:8px;vertical-align:middle;" />'
        return mark_safe(f'{img_tag}<strong>{obj.product.name}</strong>')
    product_preview.short_description = "Sản phẩm trong giỏ"

    def customer_info(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        phone = getattr(obj.user.profile, 'phone_number', '') if hasattr(obj.user, 'profile') else ''
        phone_str = f" | {phone}" if phone else ""
        return mark_safe(f"<strong>{name}</strong><br><small style='color:#64748b;'>@{obj.user.username}{phone_str}</small>")
    customer_info.short_description = "Khách hàng"

    def unit_price_display(self, obj):
        return f"{intcomma(obj.get_unit_price())} VNĐ"
    unit_price_display.short_description = "Đơn giá"

    def subtotal_display(self, obj):
        return mark_safe(f"<strong style='color:#4338ca;'>{intcomma(obj.subtotal())} VNĐ</strong>")
    subtotal_display.short_description = "Tạm tính"

    def created_at_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")
    created_at_display.short_description = "Thời gian thêm"


# Đăng ký thông tin địa lý Việt Nam
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'district_count']
    search_fields = ['name', 'code']
    list_per_page = 25

    def district_count(self, obj):
        return obj.districts.count()
    district_count.short_description = "Số Quận/Huyện"


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'province', 'ward_count']
    list_filter = ['province']
    search_fields = ['name', 'code', 'province__name']
    list_per_page = 25

    def ward_count(self, obj):
        return obj.wards.count()
    ward_count.short_description = "Số Phường/Xã"


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'district', 'province_name']
    list_filter = ['district__province']
    search_fields = ['name', 'code', 'district__name']
    list_per_page = 25

    def province_name(self, obj):
        return obj.district.province.name if obj.district and obj.district.province else "—"
    province_name.short_description = "Tỉnh / Thành phố"
