from django.db.models import Model, ForeignKey, SET_NULL, DateTimeField, DecimalField, PositiveIntegerField, CASCADE, \
    CharField, EmailField
from accounts.models import UserProfile, Address
from products.models import Product


class Order(Model):
    ORDER_STATES = [
        ('PENDING', 'Čeká na vyřízení'),
        ('SHIPPING', 'Na cestě'),
        ('COMPLETED', 'Dokončeno'),
        ('CANCELLED', 'Zrušeno'),
    ]

    customer = ForeignKey(UserProfile, on_delete=SET_NULL, null=True, blank=True, related_name='orders')
    guest_email = EmailField(null=True, blank=True)
    order_state = CharField(max_length=20, choices=ORDER_STATES, default='PENDING')
    order_creation_datetime = DateTimeField(auto_now_add=True)
    total_price = DecimalField(max_digits=10, decimal_places=2)
    billing_address = ForeignKey(Address, on_delete=SET_NULL, null=True, blank=True, related_name='billing_orders')
    shipping_address = ForeignKey(Address, on_delete=SET_NULL, null=True, blank=True, related_name='shipping_orders')

    def __repr__(self):
        customer_str = self.customer.username if self.customer else "GUEST"
        return (
            f"Order(id={self.id}, customer={customer_str}, state={self.order_state}, "
            f"total_price={self.total_price}, created={self.order_creation_datetime})"
        )

    def __str__(self):
        customer_str = self.customer.username if self.customer else "GUEST"
        return f"Order #{self.id} - {customer_str}"


class OrderProduct(Model):
    order = ForeignKey(Order, on_delete=CASCADE, related_name='items')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='order_items')
    quantity = PositiveIntegerField()
    price_per_item = DecimalField(max_digits=10, decimal_places=2)
    note = CharField(max_length=500, blank=True, null=True)

    def __repr__(self):
        customer_str = self.order.customer.username if self.order.customer else "GUEST"
        return (
            f"OrderProduct(order_id={self.order.id}, customer={customer_str}, product={self.product.product_name}, "
            f"quantity={self.quantity}, price_per_item={self.price_per_item})"
        )

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity} (Order #{self.order.id})"
