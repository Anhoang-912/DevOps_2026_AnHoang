from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib import messages
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import (
    Product, Category, CartItem, Order, OrderItem, Review, 
    Profile, Color, ProductImage, Province, District, Ward
)

# Cấu hình branding Django Admin
admin.site.site_header = "Hệ thống Quản trị E-Commerce"
admin.site.site_title = "Quản trị Shop An Hoang"
admin.site.index_title = "Bảng điều khiển quản trị"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['color', 'image', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="admin-thumb" style="width: 50px; height: 50px;" />')
        return "Chưa có ảnh"
    image_preview.short_description = "Xem trước"


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
        'image_preview', 'name', 'category', 'price', 
        'discount_percent', 'discount_price_display', 'rating_display'
    ]
    list_editable = ['price', 'discount_percent', 'category']
    list_filter = ['category', 'discount_percent']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]
    filter_horizontal = ('colors',)
    list_per_page = 20
    actions = ['apply_10_percent_discount', 'apply_20_percent_discount', 'clear_discount']

    fieldsets = (
        ('1. Thông tin cơ bản', {
            'fields': ('name', 'category', 'description')
        }),
        ('2. Giá cả & Khuyến mãi', {
            'fields': ('price', 'discount_percent')
        }),
        ('3. Hình ảnh & Màu sắc', {
            'fields': ('image', 'colors')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="admin-thumb" title="{obj.name}" />')
        return mark_safe('<div style="width:44px; height:44px; background:#f1f5f9; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#94a3b8; font-size:10px;">No pic</div>')
    image_preview.short_description = "Hình ảnh"

    def discount_price_display(self, obj):
        if obj.has_discount:
            return mark_safe(f'<strong style="color:#ef4444;">{intcomma(obj.discount_price)} ₫</strong> <span class="admin-badge badge-discount">-{obj.discount_percent}%</span>')
        return mark_safe(f'{intcomma(obj.price)} ₫')
    discount_price_display.short_description = "Giá sau giảm"

    def rating_display(self, obj):
        stars = round(obj.rating_avg)
        star_str = "★" * stars + "☆" * (5 - stars)
        return mark_safe(f'<span class="admin-stars">{star_str}</span> <small>({obj.rating_count})</small>')
    rating_display.short_description = "Đánh giá"

    # Actions giảm giá nhanh
    @admin.action(description="⚡ Áp dụng giảm giá 10%% cho các sản phẩm đã chọn")
    def apply_10_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=10)
        messages.success(request, f"Đã áp dụng giảm giá 10% cho {updated} sản phẩm.")

    @admin.action(description="⚡ Áp dụng giảm giá 20%% cho các sản phẩm đã chọn")
    def apply_20_percent_discount(self, request, queryset):
        updated = queryset.update(discount_percent=20)
        messages.success(request, f"Đã áp dụng giảm giá 20% cho {updated} sản phẩm.")

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
        'total_display', 'payment_badge', 'status', 'created_at_display'
    ]
    list_editable = ['status']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['id', 'full_name', 'phone', 'address', 'user__username', 'user__email', 'items__product__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

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


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'color_preview']
    search_fields = ['name']

    def color_preview(self, obj):
        return mark_safe(f'<div style="width:28px; height:28px; border-radius:6px; background-color:{obj.code}; border:1px solid #ccc;"></div>')
    color_preview.short_description = "Màu xem trước"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'image_thumb')
    list_filter = ('product', 'color')
    search_fields = ('product__name', 'color__name')

    def image_thumb(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="admin-thumb" />')
        return "—"
    image_thumb.short_description = "Xem trước"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_info', 'product_preview', 'color_badge', 
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

    def color_badge(self, obj):
        if obj.color:
            return mark_safe(f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background-color:{obj.color.code};border:1px solid #ccc;vertical-align:middle;margin-right:4px;"></span> {obj.color.name}')
        return "—"
    color_badge.short_description = "Màu"

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
