from order import Order, Sale
import load_helper as dat_loader
import random
import time
from users import Customer

order_dat = dat_loader.load_data("Orders")
order_id = order_dat["id"]
order_list = order_dat["data"]
product_list = dat_loader.load_data("Products")["data"]
sale_dat = dat_loader.load_data("Sales")
sale_id = sale_dat["id"]
sale_list = sale_dat["data"]
user_list = dat_loader.load_data("Users")["data"]
cus_list = []
for user in user_list:
  if isinstance(user, Customer):
    cus_list.append(user)

for user in cus_list:
  ts_now = 1609459200
  for y in range(0, 5):
    ts_now -= 31556952
    for x in range(0, 10):
      ts = ts_now
      month = random.randint(0, 11)
      ts += 2629746 * month
      total = 0
      s_list = []
      for z in range(0, random.randint(2, 4)):
        product = random.choice(product_list)
        if len(s_list) != 0:
          while True:
            counter = 0
            for sale in s_list:
              if sale.product.get_id() == product.get_id():
                product = random.choice(product_list)
              else:
                counter += 1
            if counter == len(s_list):
              break
        s = Sale(sale_id, product, random.randint(1, 5), ts)
        sale_id += 1
        sale_list.append(s)
        s_list.append(s)
      for sale in s_list:
        total += float(sale.sub_total)
      o = Order(order_id, s_list, str(round(total, 2)), user, ts)
      ran_status = random.randint(1, 3)
      if ran_status == 1:
        o.mark_shipped()
      elif ran_status == 2:
        o.mark_shipped()
        o.mark_complete()
      order_id += 1
      order_list.append(o)


dat_loader.write_data("Sales", sale_list)
dat_loader.write_data("Orders", order_list)