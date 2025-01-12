from random import randint, choice
from accounts.models import UserProfile  # Použijeme vlastní model uživatele
from products.models import Product, ProductReview

# Generování testovacích uživatelů
for i in range(5):
    UserProfile.objects.get_or_create(
        username=f"test_user_{i}",
        defaults={
            "email": f"test_user_{i}@example.com",
            "password": "password123"
        }
    )

# Vyberte produkt s ID 24
product_id = 24  # Zadejte konkrétní ID produktu
try:
    product = Product.objects.get(pk=product_id)
except Product.DoesNotExist:
    print(f"Produkt s ID {product_id} neexistuje. Nejprve vytvořte produkt s tímto ID.")
    exit()

# Generování náhodných hodnocení
users = UserProfile.objects.all()
comments = [
    "Skvělý produkt, moc se mi líbí!",
    "Byl jsem spokojen, doporučuji všem.",
    "Průměrný produkt, mohl by být lepší.",
    "Naprosto úžasné! 5 hvězdiček!",
    "Nedoporučuji, nesplnilo očekávání.",
    "Velmi dobrá kvalita za tu cenu.",
    "Určitě bych koupil znovu.",
    "Nejlepší věc, kterou jsem kdy koupil!",
    "Bylo to v pořádku, ale čekal jsem víc.",
    "Hodně dobrý produkt, stojí za to."
]

for _ in range(20):
    reviewer = choice(users)
    rating = randint(1, 5)
    comment = choice(comments)

    ProductReview.objects.create(
        product=product,
        reviewer=reviewer,
        rating=rating,
        comment=comment
    )

print(f"Hodnocení byla úspěšně přidána do databáze pod produkt s ID {product_id}.")
