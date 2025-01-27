from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, CharField, TextField, URLField, ForeignKey, DecimalField, IntegerField, \
    DateTimeField, PositiveIntegerField, SET_NULL, CASCADE, SET_DEFAULT
from django.template.defaultfilters import slugify


# from accounts.models import UserProfile


class Category(Model):
    category_name = CharField(max_length=50, null=False, blank=False, unique=True)
    category_description = TextField(null=True, blank=True)
    category_view = URLField(null=True, blank=True)
    category_parent = ForeignKey(
        'self', on_delete=SET_NULL, null=True, blank=True, related_name='subcategories'
    )

    class Meta:
        ordering = ['category_name']
        verbose_name_plural = "categories"

    def __repr__(self):
        return f"Category(category_name={self.category_name}, category_parent_id={self.category_parent_id})"

    def __str__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.category_view:
            self.category_view = f'/{slugify(self.category_name)}/'
        super().save(*args, **kwargs)


class Producer(Model):
    producer_name = CharField(max_length=50, null=False, blank=False, unique=True)
    producer_description = TextField(null=True, blank=True)
    producer_view = URLField(null=True, blank=True)

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
    product_short_description = TextField(null=False, blank=False)
    product_long_description = TextField(null=False, blank=False)
    product_view = URLField(null=True, blank=True)
    category = ForeignKey(Category, default=0, on_delete=SET_DEFAULT, null=False, blank=False, related_name='categories')
    price = DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    # Producer exists only for merchantdise product_type.
    producer = ForeignKey(Producer, default=0, on_delete=SET_DEFAULT, null=True, blank=True, related_name='producers')
    # A value will always be a number (never NULL).
    stock_availability = PositiveIntegerField(default=0, null=False, blank=True)

    class Meta:
        ordering = ['product_name']

    def __repr__(self):
        return f"Product(product_name={self.product_name}, price={self.price})"

    def __str__(self):
        return f"{self.product_name} ({self.price} Kč)"

    def available_stock(self):
        return max(self.stock_availability, 0)


class ProductReview(Model):
    product = ForeignKey(Product, on_delete=CASCADE, null=False, blank=False, related_name='product_reviews')
    reviewer = ForeignKey("accounts.UserProfile", on_delete=SET_NULL, null=True, blank=True, related_name="product_reviews_reviewer")
    rating = IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = TextField(null=True, blank=True)
    review_creation_datetime = DateTimeField(auto_now_add=True)
    review_updated_datetime = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_updated_datetime']

    def __repr__(self):
        reviewer_name = self.reviewer.username if self.reviewer else "Unknown"
        return (f"ProductReview(product={self.product.product_name}, reviewer={reviewer_name}, "
                f"rating={self.rating}, comment={self.comment})")

    def __str__(self):
        reviewer_name = self.reviewer.username if self.reviewer else "Unknown"
        return f"Review for {self.product.product_name} by {reviewer_name}"


class TrainerReview(Model):
    trainer = ForeignKey("accounts.UserProfile", on_delete=CASCADE, null=False, blank=False, related_name='trainer_reviews')
    reviewer = ForeignKey("accounts.UserProfile", on_delete=SET_NULL, null=True, blank=True, related_name="trainer_reviews_reviewer")
    rating = IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = TextField(null=True, blank=True)
    review_creation_datetime = DateTimeField(auto_now_add=True)
    review_updated_datetime = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_updated_datetime']

    def __repr__(self):
        reviewer_name = self.reviewer.username if self.reviewer else "Unknown"
        return (f"TrainerReview(trainer={self.trainer.full_name()}, reviewer={reviewer_name}, "
                f"rating={self.rating}, comment={self.comment})")

    def __str__(self):
        reviewer_name = self.reviewer.username if self.reviewer else "Unknown"
        return f"Review for {self.trainer.full_name()} by {reviewer_name}"
