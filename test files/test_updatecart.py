import load_helper as dat_loader

cart = dat_loader.load_data("Carts")["data"][0]

cart.update_item(0, 4)
dat_loader.write_data("Carts", [cart], False)