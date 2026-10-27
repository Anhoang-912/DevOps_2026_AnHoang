import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Dọn dẹp ảnh iPhone 16 Pro Max và xóa các sản phẩm trùng lặp'

    def handle(self, *args, **options):
        # 1. Đảm bảo ảnh iPhone 16 thật
        src_img = os.path.join(settings.MEDIA_ROOT, 'products', 'ip-16e.jpg')
        nhi_img = os.path.join(settings.MEDIA_ROOT, 'products', 'Nhi_4.jpg')
        ip3_img = os.path.join(settings.MEDIA_ROOT, 'products', 'ip3.jpg')

        if os.path.exists(src_img):
            try:
                shutil.copyfile(src_img, nhi_img)
                shutil.copyfile(src_img, ip3_img)
                self.stdout.write(self.style.SUCCESS('Da sao chep anh dien thoai cho Nhi_4.jpg va ip3.jpg'))
            except Exception as e:
                self.stdout.write(f'Loi sao chep anh: {e}')

        # 2. Cập nhật iPhone 16 Pro Max vào đúng danh mục Điện thoại (ID: 1) và ảnh chuẩn
        cat_dt = Category.objects.filter(id=1).first() or Category.objects.first()
        iphones = list(Product.objects.filter(name__icontains='iphone 16'))
        if iphones:
            for p in iphones:
                p.image = 'products/ip-16e.jpg'
                if cat_dt:
                    p.category = cat_dt
                p.save()
            # Nếu có nhiều hơn 1 bản ghi iPhone 16, giữ lại 1 bản
            if len(iphones) > 1:
                for extra in iphones[1:]:
                    extra.delete()
            self.stdout.write(self.style.SUCCESS('Da cap nhat anh dien thoai va danh muc cho iPhone 16 Pro Max'))

        # 3. Xóa sản phẩm trùng lặp DevOps / DevOps1 (chỉ giữ lại 1 sản phẩm)
        devops_prods = list(Product.objects.filter(name__icontains='devops'))
        if len(devops_prods) > 1:
            for extra in devops_prods[1:]:
                self.stdout.write(self.style.WARNING(f'Xoa san pham trung lap: {extra.name} (ID: {extra.id})'))
                extra.delete()

        self.stdout.write(self.style.SUCCESS(f'Hoan thanh don dep! Tong so san pham: {Product.objects.count()}'))
