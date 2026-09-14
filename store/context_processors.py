from .models import CartItem, Category, Order, Product
from django.contrib.auth.models import User
from django.db.models import Sum, Count

def store_context(request):
    """
    Context processor cung cấp các biến chung cho toàn bộ website:
    - cart_items_count: Số lượng sản phẩm trong giỏ hàng của user
    - nav_categories: Danh sách tất cả danh mục sản phẩm
    - admin_stats: Thống kê số liệu cho Admin Dashboard (nếu là staff)
    """
    context = {
        'nav_categories': Category.objects.all(),
    }
    
    # Tính số lượng sản phẩm trong giỏ hàng
    if request.user.is_authenticated:
        context['cart_items_count'] = CartItem.objects.filter(user=request.user).count()
    else:
        context['cart_items_count'] = 0

    # Nếu truy cập trang quản trị hoặc người dùng là staff, cung cấp thống kê số liệu
    if request.user.is_authenticated and request.user.is_staff:
        # Doanh thu từ các đơn hàng không bị hủy
        valid_orders = Order.objects.exclude(status='cancelled')
        total_revenue = valid_orders.aggregate(total=Sum('total'))['total'] or 0
        
        # Đơn hàng
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        
        # Sản phẩm
        total_products = Product.objects.count()
        discounted_products = Product.objects.filter(discount_percent__gt=0).count()
        
        # Khách hàng
        total_customers = User.objects.filter(is_staff=False).count()

        # Giỏ hàng chưa thanh toán (Cart Items)
        active_cart_items = CartItem.objects.count()
        active_cart_users = CartItem.objects.values('user').distinct().count()
        
        # Đơn hàng gần đây (6 đơn)
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:6]
        
        context['admin_stats'] = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_products': total_products,
            'discounted_products': discounted_products,
            'total_customers': total_customers,
            'active_cart_items': active_cart_items,
            'active_cart_users': active_cart_users,
            'recent_orders': recent_orders,
        }
        
    return context
