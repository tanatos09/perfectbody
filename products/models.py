from django.db.models import Model, CharField, TextField, URLField, ForeignKey, DecimalField, IntegerField, DateTimeField, PositiveIntegerField, SET_NULL, CASCADE
# from accounts.models import UserProfile

class Category(Model):
    category_name = CharField(max_length=50, null=False, blank=False, unique=True)
    category_description = TextField(null=True, blank=True)
    category_parent = ForeignKey('self', on_delete=SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        ordering = ['category_name']
        verbose_name_plural = "categories"

    def __repr__(self):
        return f"Category(category_name={self.category_name}, category_parent_id={self.category_parent_id})"

    def __str__(self):
        return self.category_name


class Producer(Model):
    producer_name = CharField(max_length=50, null=False, blank=False, unique=True)

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

    product_type = CharField(max_length=12, null=False, blank=False, choices=PRODUCT_TYPES) # max_length == Merchantdise
    product_name = CharField(max_length=100, null=False, blank=False)
    product_description = TextField(null=True, blank=True)
    product_view = URLField(null=True, blank=True)
    category = ForeignKey(Category, on_delete=SET_NULL, null=True, blank=True, related_name='categories')
    price = DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    producer = ForeignKey(Producer, on_delete=SET_NULL, null=True, blank=True, related_name='producers') # producer is filled only for merchantdise product_type
    stock_availability = PositiveIntegerField(default=0, null=False, blank=True) # a value will always be a number (never NULL)

    class Meta:
        ordering = ['product_name']

    def __repr__(self):
        return f"Product(product_name={self.product_name}, price={self.price})"

    def __str__(self):
        return f"{self.product_name} ({self.price} Kč)"


# class ProductReview(Model):
#     product = ForeignKey(Product, on_delete=CASCADE, null=False, blank=False, related_name='reviews')
#     reviewer = ForeignKey(accounts.UserProfile, on_delete=SET_NULL, null=False, blank=False, related_name="reviews")
#     rating = IntegerField(null=True, blank=True)
#     comment = TextField(null=True, blank=True)
#     review_creation_datetime = DateTimeField(auto_now_add=True)
#     review_updated_datetime = DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-review_updated_datetime']
#
#     def __repr__(self):
#         return (f"ProductReview(product={self.product}, reviewer={self.reviewer}, "
#                 f"rating={self.rating}, comment={self.comment})")
#
#     def __str__(self):
#         return f"Review for {self.product.product_name} by {self.reviewer.userprofile.login}"
