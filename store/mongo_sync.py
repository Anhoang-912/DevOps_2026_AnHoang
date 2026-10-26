import time
from decimal import Decimal

_last_sync_time = 0
SYNC_THROTTLE_SECONDS = 3

def sync_products_from_mongo(force=False):
    """
    Tự động đồng bộ sản phẩm từ MongoDB Atlas (Compass) về cơ sở dữ liệu của website.
    Mỗi khi người dùng thêm/sửa sản phẩm trên MongoDB Compass và tải lại trang,
    dữ liệu mới sẽ được cập nhật ngay lập tức lên web EC2.
    """
    global _last_sync_time
    now = time.time()
    if not force and (now - _last_sync_time < SYNC_THROTTLE_SECONDS):
        return

    _last_sync_time = now

    try:
        from pymongo import MongoClient
        from store.models import Product, Category

        uri = 'mongodb+srv://an2k52012_db_user:Anhoang.912@cluster0.hrrmitg.mongodb.net/?retryWrites=true&w=majority'
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        db = client['ecommerce_db']

        coll_names = db.list_collection_names()
        coll = None
        if 'store_product' in coll_names:
            coll = db['store_product']
        elif 'products' in coll_names:
            coll = db['products']

        if coll is None:
            return

        mongo_docs = list(coll.find())
        if not mongo_docs:
            return

        for doc in mongo_docs:
            name = doc.get('name')
            if not name:
                continue

            # Xử lý danh mục
            cat_id = doc.get('category_id') or 1
            cat = Category.objects.filter(id=cat_id).first() or Category.objects.first()

            # Xử lý giá tiền
            raw_price = doc.get('price', 0)
            try:
                price = Decimal(str(raw_price))
            except Exception:
                price = Decimal(0)

            discount = int(doc.get('discount_percent', 0) or 0)
            description = doc.get('description', '')
            image = str(doc.get('image', ''))

            product = Product.objects.filter(name=name).first()
            if product:
                product.price = price
                product.discount_percent = discount
                product.description = description
                if image:
                    product.image = image
                if cat:
                    product.category = cat
                product.save()
            else:
                Product.objects.create(
                    name=name,
                    category=cat,
                    price=price,
                    discount_percent=discount,
                    description=description,
                    image=image
                )
    except Exception:
        # Nếu có lỗi mạng với MongoDB thì bỏ qua an toàn, không làm gián đoạn web
        pass
