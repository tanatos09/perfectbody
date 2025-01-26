# PerfectBody project

## Introduction (EN)
The PerfectBody project is a modern e-commerce platform focused on fitness and a healthy lifestyle. In addition to selling products, it provides a space for trainers to register, showcase their services, and connect with clients. Trainer registration includes an approval process managed by an administrator, ensuring control over the quality of the offered services. The system features user-friendly functionalities such as advanced filtering, customer registration, dynamic cart management, customer reviews for products and trainers, and a comprehensive admin interface for content and user management.

## Představení (CZ)
Projekt PerfectBody je moderní e-commerce platforma zaměřená na fitness a zdravý životní styl. Kromě prodeje zboží, poskytuje prostor pro trenéry. Ti se mohou registrovat, prezentovat své služby a propojit se s klienty. Registrace trenérů je doplněna schvalovacím procesem spravovaným administrátorem, což umožňuje kontrolu nad kvalitou nabízených služeb. Systém zahrnuje uživatelsky přívětivé funkce, jako je pokročilé filtrování, registrace zákazníka, dynamická správa košíku, zákaznické hodnocení zboží a trenérů, a plnohodnotné administrátorské rozhraní pro správu obsahu a uživatelů.

## Functionalities (EN)
### 1. User Account
- **User Registration:** Standard user registration, including multi-step registration for trainers.
- **User Login and Logout.**
- **Profile Management:**
  - **Personal Information:** Ability to edit name, addresses, and password.
  - **Avatar URL:** Each user can add or update the URL of their avatar.
  - **Additional Images for Trainers:** Trainers can add extra image URLs to their profile, which will be displayed on their detailed page.
- **Address Auto-fill:** If a user has entered an address before, it will automatically pre-fill for future orders.
- **Password Change:** Users can change their password using a secure and simple form.
- **Existence Check** Validation to ensure the username or email already exists in the system.
- **Password Encryption:** User passwords are secured through hashing.
- **Trainer Content Approval:**
  - **Trainer Description Approval:** Any changes to the trainer's short or long description must be approved by an admin.
  - **Trainer Services Approval:** Edits to service descriptions or new service additions await admin approval.
- **Order History:** Display of past orders overview.

### 2. Product and Service Catalog
- **Display of Main Categories and Subcategories.**
- **Product Details:** Display of description, price, reviews, and availability.
- **Product Filtering and Sorting:** By category, gender (men’s/women’s), and price.
- **Service Support:** Display of approved trainers for specific services.

### 3. Trainers
- **Trainer Display:** Trainers are only shown in listings and searches if they have at least one approved service.
- **Trainer Detail:**
  - Display of approved services, ratings, and the ability to add a review.
  - Display of the trainer's avatar and additional uploaded images.

### 4. Dynamic Cart
- **AJAX Add to Cart:**
  - After adding a product to the cart, a confirmation message displays that the product has been successfully added.
  - The cart icon immediately updates the item count.
  - **Cart Preview:** Hovering over the cart icon shows a dynamic preview with the cart contents, total price, a link to cart details, and options to modify items.
- **Cart Modification:**
  - Updating quantities, adding notes to items, and removing items from the cart.

### 5. Orders
- **Order Creation:** Processing the cart and selecting delivery and billing addresses.
- **Billing Address Option:** Users can specify a different billing address during checkout.
- **Address Auto-fill:** If the user has a saved address, it is used as the default for new orders.
- **Order Summary:** Display of details before confirmation.
- **Order Confirmation:**
  - Upon confirmation, products are automatically deducted from stock inventory.
  - If a product is out of stock or inventory is insufficient, the order is not processed, and the user is notified.
- **Order Cancellation:**
  - Users can cancel an order if it has not yet been shipped.
  - Upon cancellation, products are automatically returned to inventory.
- **Order History:** Users can view details of past orders.

### 6. Reviews
- **Ability to add and edit reviews for products, services, and trainers.**
- **Admin Approval and Deletion of Reviews.**

### 7. Admin Features
- **Product Management:** Adding, editing, and deleting products.
- **Category Management:** Creating and deleting empty categories.
- **User Management:**
  - **Superadmin:**
    - Can grant or revoke admin and superadmin rights to other users.
    - Can edit or delete accounts of other admins and superadmins.
  - **Admin:**
    - Cannot edit or delete accounts of other admins or superadmins.
    - Has rights to manage regular user accounts and trainer accounts.
- **Trainer Content Approval:**
  - Approve or reject changes to trainer descriptions and their services.

### 8. Search
- **Full-text Search:** For products, services, and trainers.
- **Trainer Condition:** Only trainers with at least one approved service are shown in search results.
- **Search Without Accents:** Searching works even without diacritics.
- **AJAX Support:** Fast, real-time search results.

### 9. Weather and Name Days
- **Display of Current Weather:** Based on the user's city or default cities (Brno, Prague, Ostrava).
- **Name Day Display:** Information on whose name day it is (based on the Czech calendar).

### 10. Other
- **Support for Multiple Product Types:** Merchandise and services.
- **Custom Error Pages:** For errors 400, 403, 404, 408, 429, 500, and 503.

## Funkcionality (CZ)

### 1. Uživatelský účet
- **Registrace uživatele:** Standardní registrace uživatelů, včetně registrace trenérů s více kroky.
- **Přihlášení a odhlášení uživatele.**
- **Správa profilu:** 
  - **Osobní údaje:** Možnost upravovat jméno, adresy a heslo.
  - **URL avataru:** Každý uživatel může přidat nebo změnit URL svého avataru.
  - **Další obrázky pro trenéry:** Trenéři mohou ke svému profilu přidat další URL obrázků, které budou viditelné na jejich detailní stránce.
- **Automatické doplňování adresy:** Pokud uživatel zadal adresu v minulosti, automaticky se předvyplní při dalších objednávkách.
- **Změna hesla:** Uživatelé mohou měnit své heslo přes jednoduchý formulář se zabezpečením.
- **Kontrola existence:** Validace, zda uživatelské jméno nebo email již existují v systému.
- **Šifrování hesel:** Hesla uživatelů jsou zabezpečena hashováním.
- **Schválení obsahu trenérů:**
  - **Schvalování popisků trenéra:** Jakékoliv změny v krátkém nebo dlouhém popisu trenéra musí být schváleny adminem.
  - **Schvalování služeb trenéra:** Úpravy popisků služeb nebo přidání nové služby čekají na schválení adminem.
- **Historie objednávek:** Zobrazení přehledu minulých objednávek.

### 2. Katalog produktů a služeb
- **Zobrazení hlavních kategorií a podkategorií.**
- **Detaily produktů:** Zobrazení popisu, ceny, recenzí a dostupnosti.
- **Filtrování a třídění produktů:** Podle kategorie, pohlaví (dámské/pánské) a ceny.
- **Podpora služeb:** Zobrazení schválených trenérů pro konkrétní služby.

### 3. Trenéři
- **Zobrazení trenérů:** Trenéři se zobrazují v nabídce a ve vyhledávání pouze tehdy, pokud mají alespoň jednu schválenou službu.
- **Detail trenéra:**
  - Zobrazení schválených služeb trenéra, hodnocení a možnost přidat recenzi.
  - Zobrazení avataru trenéra a dalších přidaných obrázků.

### 4. Dynamický košík
- **AJAX přidávání do košíku:** 
  - Po přidání produktu do košíku se zobrazí potvrzovací hláška, že byl produkt úspěšně přidán.
  - Ikona košíku okamžitě aktualizuje počet položek v košíku.
  - **Náhled košíku:** Při najetí na ikonu košíku se zobrazí dynamický náhled s obsahem košíku, celkovou cenou, odkazem na detail košíku a možností úpravy položek.
- **Možnost úpravy košíku:**
  - Aktualizace množství, poznámek u položek a odebrání položek z košíku.

### 5. Objednávky
- **Vytvoření objednávky:** Zpracování košíku a výběr doručovací a fakturační adresy.
- **Možnost přidat fakturační adresu:** Uživatel může při objednávce zadat odlišnou fakturační adresu.
- **Automatické doplňování adres:** Pokud má uživatel uloženou adresu, použije se jako výchozí pro novou objednávku.
- **Shrnutí objednávky:** Zobrazení detailů před potvrzením.
- **Potvrzení objednávky:** 
  - Při potvrzení objednávky se automaticky odečtou produkty ze skladových zásob.
  - Pokud produkt není skladem nebo je zásoba nedostatečná, objednávka se nezpracuje a uživatel dostane upozornění.
- **Stornování objednávky:** 
  - Uživatel může zrušit objednávku, pokud ještě nebyla odeslána.
  - Při zrušení se produkty automaticky vrací zpět na sklad.
- **Historie objednávek:** Možnost prohlédnout detaily minulých objednávek.

### 6. Recenze
- **Možnost přidávat a upravovat hodnocení produktů, služeb a trenérů.**
- **Schválení a mazání recenzí adminem.**

### 7. Admin funkce
- **Správa produktů:** Přidávání, úprava a mazání produktů.
- **Správa kategorií:** Vytváření a mazání prázdných kategorií.
- **Správa uživatelů:**
  - **Superadmin:** 
    - Může přidělovat nebo odebírat admin a superadmin práva jiným uživatelům.
    - Může upravovat nebo mazat účty ostatních adminů i superadminů.
  - **Admin:**
    - Nemůže upravovat ani mazat účty jiných adminů nebo superadminů.
    - Má práva spravovat běžné uživatelské účty a trenérské účty.
- **Schvalování trenérského obsahu:**
  - Schválení nebo zamítnutí úprav popisků trenérů a jejich služeb.

### 8. Vyhledávání
- **Full-textové vyhledávání:** Produkty, služby a trenéři.
- **Podmínka pro trenéry:** Zobrazení pouze trenérů se schválenou alespoň jednou službou.
- **Vyhledávání bez diakritiky:** Vyhledávání funguje i bez použití háčků a čárek.
- **AJAX podpora:** Rychlé vyhledávací výsledky v reálném čase.

### 9. Počasí a jmeniny
- **Zobrazení aktuálního počasí:** Na základě města uživatele nebo výchozích měst (Brno, Praha, Ostrava).
- **Zobrazení jmenin:** Informace o tom, kdo má dnes svátek (dle českého kalendáře).

### 10. Ostatní
- **Podpora více typů produktů:** Produkty (merchandise) a služby.
- **Vlastní chybové stránky:** Pro chyby 400, 403, 404, 408, 429, 500 a 503.

## Database

- [x] user_profile
  - [x] id
  - [x] avatar
  - [x] phone
  - [x] preferred_channel
  - [x] profile_picture
  - [x] pending_profile_picture
  - [x] trainer_short_description
  - [x] trainer_long_description
  - [x] pending_trainer_short_description
  - [x] pending_trainer_long_description
  - [x] date_of_birth
  - [x] created_at
  - [x] account_type
- [x] address
  - [x] id
  - [x] user_id (1:n -> user)
  - [x] first_name
  - [x] last_name
  - [x] street
  - [x] street_number
  - [x] city
  - [x] postal_code
  - [x] country
  - [x] email
- [x] product
  - [x] id
  - [x] product_type
  - [x] product_name
  - [x] product_short_description
  - [x] product_long_description
  - [x] product_view
  - [x] category_id (1:n -> category)
  - [x] price
  - [x] producer_id (1:n -> producer)
  - [x] stock_availability
- [x] category
  - [x] id
  - [x] category_name
  - [x] category_description
  - [x] category_view
  - [x] category_parent_id (1:n -> category)
- [x] trainers_services
  - [x] id
  - [x] trainers (n:m -> user)
  - [x] services (n:m -> product)
  - [x] trainer_short_description
  - [x] trainer_long_description
  - [x] is_approved
- [x] order
  - [x] id
  - [x] customer_id (1:n -> user)
  - [x] guest_email
  - [x] order_state
  - [x] order_creation_datetime
  - [x] total_price
  - [x] billing_address_id (1:n -> address)
  - [x] shipping_address_id (1:n -> address)
- [x] orders_products
  - [x] id
  - [x] orders (n:m -> order)
  - [x] product_id (1:n -> product)
  - [x] quantity
  - [x] price_per_item
  - [x] note
- [x] producer
  - [x] id
  - [x] producer_name
  - [x] producer_description
  - [x] producer_view
- [x] product_review
  - [x] id
  - [x] product_id (1:n -> product)
  - [x] reviewer_id (1:n -> user)
  - [x] rating
  - [x] comment
  - [x] review_creation_datetime
  - [x] review_update_datetime
- [x] trainer_review
  - [x] id
  - [x] trainer_id (1:n -> user)
  - [x] reviewer_id (1:n -> user)
  - [x] rating
  - [x] comment
  - [x] review_creation_datetime
  - [x] review_update_datetime

## Data sources
### Photos
- https://unsplash.com/
- https://www.freepik.com/
### Database content and producers logos
- https://chatgpt.com/
### Images storage
- https://ibb.co/album/QvjY3B