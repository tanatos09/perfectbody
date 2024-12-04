from django.db.models import Model, CharField, TextField, URLField, ForeignKey, DecimalField, IntegerField, DateTimeField, CASCADE
# from accounts.models import UserProfile

class Category(Model):
    category_name = CharField(max_length=100, unique=True)
    category_description = TextField()
    # category_parent_id = ForeignKey(Category)

class Producer(Model):
    produce_name = CharField(max_length=100, unique=True)

class Product(Model):
    product_type = CharField(max_length=20)
    product_name = CharField(max_length=255)
    product_description = TextField()
    product_view = URLField(blank=True, null=True)
    category_id = ForeignKey(Category)
    price = DecimalField(max_digits=10, decimal_places=2)
    producer = ForeignKey(Producer)

class ProductReview(Model):
    product_id = ForeignKey(Product, on_delete=CASCADE, null=False, blank=False)
    # reviewer_id = ForeignKey(UserProfile)
    rating = IntegerField(null=True, blank=True)
    comment = TextField(null=True, blank=True)
    review_creation_datetime = DateTimeField(auto_now_add=True)
