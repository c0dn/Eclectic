import load_helper as dat_loader
import random

cart_list = dat_loader.load_data("Carts")["data"]
product_list = dat_loader.load_data("Products")["data"]
for cart in cart_list:
  for x in range(0, 4):
    product = random.choice(product_list)
    cart.add_item(product.get_id(), random.randint(1, 4))

dat_loader.write_data("Carts", cart_list, False)
