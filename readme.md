# PerfectBody project

Online store with admin panel.

## Database

- [ ] user
  - [ ] id
  - [ ] account_type
  - [ ] role
  - [ ] login
  - [ ] password
  - [ ] avatar
  - [ ] first_name
  - [ ] last_name
  - [ ] phone_number
  - [ ] email
  - [ ] preferred_communication_channel
  - [ ] user_creation_time
- [ ] address
  - [ ] id
  - [ ] street
  - [ ] town
  - [ ] postal_code
  - [ ] country
  - [ ] user_id (1:n -> user)
  - [ ] order_id (1:n -> order)
- [ ] product
  - [ ] id
  - [ ] product_type
  - [ ] product_name
  - [ ] product_description
  - [ ] product_view
  - [ ] category_id (1:n -> category)
  - [ ] price
  - [ ] producer_id (1:n -> producer)
  - [ ] stock_availability
- [ ] category
  - [ ] id
  - [ ] category_name
  - [ ] category_description
  - [ ] category_parent_id (1:n -> category)
- [ ] trainers_services
  - [ ] id
  - [ ] trainers (n:m -> user)
  - [ ] services (n:m -> product)
- [ ] order
  - [ ] id
  - [ ] user_id (1:n -> user)
  - [ ] state
  - [ ] order_creation_time
  - [ ] total_price
  - [ ] billing_address_id (1:n -> address)
  - [ ] shipping_address_id (1:n -> address)
- [ ] orders_products
  - [ ] id
  - [ ] orders (n:m -> order)
  - [ ] products (n:m -> product)
  - [ ] quantity
  - [ ] price_per_piece
- [ ] producer
  - [ ] id
  - [ ] producer_name
- [ ] review
  - [ ] id
  - [ ] product_id (1:n -> product)
  - [ ] reviewer (1:n -> user)
  - [ ] rating
  - [ ] comment
  - [ ] time