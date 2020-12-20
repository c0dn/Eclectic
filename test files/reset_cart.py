import load_helper as dat_loader
from order import Cart

dat_loader.write_data("Carts", [])
carts = dat_loader.load_data("Carts")["data"]
cart_dat = dat_loader.load_data("Carts")
cart_id = cart_dat["id"]
cart_list = cart_dat["data"]
c = Cart(cart_id, 1, [])
cart_list.append(c)
dat_loader.write_data("Carts", cart_list)