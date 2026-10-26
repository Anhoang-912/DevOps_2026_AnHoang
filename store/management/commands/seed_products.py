from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Tạo đầy đủ 40 sản phẩm mẫu chất lượng cao cho cửa hàng'

    def handle(self, *args, **options):
        # Đảm bảo các danh mục tồn tại
        categories = {
            1: 'Điện thoại',
            2: 'Máy Tính',
            3: 'Tablet',
            4: 'Phụ Kiện',
            5: 'Smartwatch',
        }
        for cid, cname in categories.items():
            Category.objects.get_or_create(id=cid, defaults={'name': cname})

        new_products_data = [
            {
                'name': 'Samsung Galaxy Note 10',
                'category_id': 1,
                'price': 6500000,
                'discount_percent': 15,
                'image': 'products/galaxy note 10.jpg',
                'description': 'Điện thoại Samsung Galaxy Note 10 thiết kế kim loại kính sang trọng, tích hợp bút S-Pen thông minh với nhiều cử chỉ không chạm, màn hình Dynamic AMOLED sắc nét cùng camera chụp đêm chuyên nghiệp.'
            },
            {
                'name': 'OPPO Reno5 5G',
                'category_id': 1,
                'price': 5200000,
                'discount_percent': 10,
                'image': 'products/oppo reno 5.jpg',
                'description': 'OPPO Reno5 5G sở hữu sạc siêu nhanh 65W SuperVOOC 2.0 đầy pin chỉ trong 35 phút, camera chân dung đêm 64MP và mặt lưng Reno Glow phủ lấp lánh chống bám vân tay.'
            },
            {
                'name': 'POCO X5 Pro 5G',
                'category_id': 1,
                'price': 6890000,
                'discount_percent': 20,
                'image': 'products/poco.jpg',
                'description': 'POCO X5 Pro 5G trang bị vi xử lý Snapdragon 778G cực mạnh, màn hình Flow AMOLED 120Hz siêu mượt và camera chính độ phân giải 108MP đỉnh cao trong tầm giá.'
            },
            {
                'name': 'Realme 9i 6GB/128GB',
                'category_id': 1,
                'price': 3500000,
                'discount_percent': 0,
                'image': 'products/realme 9i.jpg',
                'description': 'Realme 9i nổi bật với chip Snapdragon 680 tiến trình 6nm tiết kiệm điện năng, viên pin khủng 5000mAh hỗ trợ sạc nhanh 33W Dart Charge cùng hệ thống loa kép stereo sống động.'
            },
            {
                'name': 'Samsung Galaxy A14 5G',
                'category_id': 1,
                'price': 3890000,
                'discount_percent': 12,
                'image': 'products/samsung galaxy a14.jpg',
                'description': 'Samsung Galaxy A14 mang đến trải nghiệm kết nối 5G tốc độ cao trong phân khúc phổ thông, màn hình rộng 6.6 inch Full HD+ 90Hz mượt mà và bộ 3 camera 50MP sắc nét.'
            },
            {
                'name': 'Xiaomi 12 Pro 5G',
                'category_id': 1,
                'price': 12990000,
                'discount_percent': 25,
                'image': 'products/xiaomi 12.jpg',
                'description': 'Flagship Xiaomi 12 Pro 5G với bộ ba camera 50MP cảm biến Sony IMX707 cao cấp, màn hình AMOLED 2K LTPO 120Hz và công nghệ sạc thần tốc 120W Xiaomi HyperCharge.'
            },
            {
                'name': 'Xiaomi Redmi Note 11',
                'category_id': 1,
                'price': 3500000,
                'discount_percent': 10,
                'image': 'products/xiaomi note 11.jpg',
                'description': 'Redmi Note 11 dòng máy quốc dân được yêu thích với tấm nền AMOLED 90Hz sống động, vi xử lý Snapdragon 680 bền bỉ và camera AI 50MP sắc nét.'
            },
            {
                'name': 'Laptop Dell Vostro 3520 i5',
                'category_id': 2,
                'price': 14500000,
                'discount_percent': 10,
                'image': 'products/lap-1.jpg',
                'description': 'Laptop văn phòng Dell Vostro 3520 trang bị chip Intel Core i5 Gen 12 mạnh mẽ, RAM 16GB đa nhiệm mượt mà, ổ cứng SSD NVMe 512GB và màn hình 15.6 inch 120Hz chống chói.'
            },
            {
                'name': 'Laptop Gaming ASUS TUF F15',
                'category_id': 2,
                'price': 21900000,
                'discount_percent': 15,
                'image': 'products/lap-2.jpg',
                'description': 'Chiến binh gaming ASUS TUF F15 trang bị card đồ họa rời NVIDIA GeForce RTX 3050, hệ thống tản nhiệt buồng hơi kép và độ bền chuẩn quân sự Mỹ MIL-STD-810H.'
            },
            {
                'name': 'Laptop MSI Modern 14 B11',
                'category_id': 2,
                'price': 13200000,
                'discount_percent': 0,
                'image': 'products/lap-3.jpg',
                'description': 'MSI Modern 14 thiết kế siêu mỏng nhẹ chỉ 1.3kg, vỏ nhôm nguyên khối Carbon Grey thời thượng, bản lề mở phẳng 180 độ và thời lượng pin bền bỉ cho cả ngày dài.'
            },
            {
                'name': 'iPad Air 5 M1 64GB WiFi',
                'category_id': 3,
                'price': 14890000,
                'discount_percent': 15,
                'image': 'products/ipad-4.jpg',
                'description': 'iPad Air 5 mang sức mạnh bùng nổ của vi xử lý Apple M1 đỉnh cao đồ họa, cổng USB-C tốc độ cao và hỗ trợ hoàn hảo Apple Pencil 2 cùng bàn phím Magic Keyboard.'
            },
            {
                'name': 'iPad Mini 6 64GB WiFi',
                'category_id': 3,
                'price': 11500000,
                'discount_percent': 10,
                'image': 'products/ipad-5.jpg',
                'description': 'iPad Mini 6 thiết kế viền mỏng toàn màn hình Liquid Retina 8.3 inch nhỏ gọn vừa lòng bàn tay, chip A15 Bionic mạnh mẽ và cảm biến Touch ID tích hợp tiện lợi trên nút nguồn.'
            },
            {
                'name': 'iPad Gen 10 10.9 inch WiFi',
                'category_id': 3,
                'price': 8990000,
                'discount_percent': 10,
                'image': 'products/ipad-6.jpg',
                'description': 'iPad Gen 10 lột xác với thiết kế viền phẳng hiện đại nhiều màu sắc cá tính, màn hình Liquid Retina tràn viền 10.9 inch và camera selfie góc siêu rộng đặt ngang thông minh.'
            },
            {
                'name': 'Củ Sạc Nhanh Anker 65W GaN',
                'category_id': 4,
                'price': 850000,
                'discount_percent': 20,
                'image': 'products/sac-4.jpg',
                'description': 'Củ sạc công nghệ GaN siêu nhỏ gọn Anker 65W, tích hợp 3 cổng sạc nhanh chuẩn PD hỗ trợ cấp nguồn cùng lúc cho cả Laptop, điện thoại iPhone và máy tính bảng mát mẻ an toàn.'
            },
            {
                'name': 'Khóa Cửa Điện Tử Thông Minh Smart Lock',
                'category_id': 4,
                'price': 1250000,
                'discount_percent': 10,
                'image': 'products/lock-1.jpg',
                'description': 'Khóa điện tử thông minh Smart Lock đa phương thức bảo mật: cảm biến vân tay siêu nhạy 0.2s, mã số chống nhìn trộm, thẻ từ và kết nối điều khiển từ xa qua ứng dụng di động.'
            },
            {
                'name': 'Apple Watch Series 9 GPS 41mm',
                'category_id': 5,
                'price': 8990000,
                'discount_percent': 10,
                'image': 'products/smw-1.jpg',
                'description': 'Apple Watch Series 9 trang bị vi xử lý S9 SiP vượt trội, tính năng chạm hai lần Double Tap kỳ diệu, màn hình Always-On siêu sáng 2000 nits và hệ thống theo dõi sức khỏe chuyên sâu.'
            }
        ]

        added = 0
        for item in new_products_data:
            cat = Category.objects.get(id=item['category_id'])
            p, created = Product.objects.get_or_create(
                name=item['name'],
                category=cat,
                defaults={
                    'price': item['price'],
                    'discount_percent': item['discount_percent'],
                    'image': item['image'],
                    'description': item['description']
                }
            )
            if created:
                added += 1
                self.stdout.write(self.style.SUCCESS(f"+ Đã thêm sản phẩm: {p.name}"))
            else:
                self.stdout.write(f"= Đã tồn tại: {p.name}")

        self.stdout.write(self.style.SUCCESS(f"Hoàn thành! Tổng số sản phẩm hiện tại: {Product.objects.count()}"))
