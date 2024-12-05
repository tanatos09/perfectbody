from django.db.models import Model, CharField, TextField, URLField, ForeignKey, DecimalField, IntegerField, DateTimeField, PositiveIntegerField, SET_NULL, CASCADE
# from accounts.models import UserProfile

class Category(Model):
    category_name = CharField(max_length=100, unique=True)
    category_description = TextField(null=True, blank=True)
    category_parent_id = ForeignKey('self', on_delete=SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        ordering = ['category_name']

    def __repr__(self):
        return f"Category(category_name={self.category_name}, category_parent_id={self.category_parent_id})"

    def __str__(self):
        return self.category_name


class Producer(Model):
    producer_name = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['producer_name']

    def __repr__(self):
        return f"Producer(producer_name={self.producer_name})"

    def __str__(self):
        return self.producer_name


class Product(Model):

    PRODUCT_TYPES = [
        ("merchantdise", "Merchantdise"),
        ("service", "Service"),
    ]

    product_type = CharField(max_length=20, choices=PRODUCT_TYPES)
    product_name = CharField(max_length=255)
    product_description = TextField()
    product_view = URLField(null=True, blank=True)
    category_id = ForeignKey(Category, on_delete=SET_NULL, null=True, blank=False, related_name='categories')
    price = DecimalField(max_digits=10, decimal_places=2)
    producer_id = ForeignKey(Producer, on_delete=SET_NULL, null=True, related_name='producers')
    stock_availability = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['product_name']

    def __repr__(self):
        return f"Product(product_name={self.product_name}, price={self.price})"

    def __str__(self):
        return f"{self.product_name} ({self.price} Kč)"


class ProductReview(Model):
    product_id = ForeignKey(Product, on_delete=CASCADE, null=False, blank=False, related_name='reviews')
    # reviewer_id = ForeignKey(UserProfile, on_delete=SET_NULL, null=True, blank=False, related_name="reviews")
    rating = IntegerField(null=True, blank=True)
    comment = TextField(null=True, blank=True)
    review_creation_datetime = DateTimeField(auto_now_add=True)
    review_updated_datetime = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_updated_datetime']

    def __repr__(self):
        return (f"ProductReview(product_id={self.product_id}, reviewer_id={self.reviewer_id}, "
                f"rating={self.rating}, comment={self.comment})")

    def __str__(self):
        return f"Review for {self.product_id.product_name} by {self.reviewer_id.username}"
