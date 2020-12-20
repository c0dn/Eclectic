import time
import pycountry
import pytz
from datetime import datetime
import load_helper as dat_loader


class Order:
  def __init__(self, id, sales, total, customer, time_created):
    self.__id = id
    self.__ordered_datetime = time_created
    self.__sales_list = sales
    self.__customer = customer
    self.total_price = total
    self.__courier = "NinjaVan"
    mapping = {country.name: country.alpha_2 for country in pycountry.countries}
    tracking = "ELC" + "%09d" % id + mapping[customer.get_country()]
    self.__tracking_number = tracking
    self.__shipped = False
    self.__delivered = False
    self.__delivery_datetime = None

  def mark_complete(self):
    if self.__shipped:
      self.__delivered = True
      obj = datetime.utcfromtimestamp(time.time()).replace(tzinfo=pytz.utc)
      local_tz = pytz.timezone("Asia/Singapore")
      local_dt = local_tz.normalize(obj.astimezone(local_tz))
      self.__delivery_datetime = local_dt.strftime("%d/%m/%Y")
    else:
      raise Exception("Item not shipped, unable to mark order as complete")

  def mark_shipped(self):
    self.__shipped = True

  def is_shipped(self):
    return self.__shipped

  def is_delivered(self):
    return self.__delivered

  def get_tracking(self):
    return self.__tracking_number

  def get_courier(self):
    return self.__courier

  def get_delivery_info(self):
    dat = {
      "tracking_no": self.__tracking_number,
      "courier": self.__courier,
      "delivered": self.__delivered,
    }
    if self.__shipped:
      dat["shipped"] = True
    else:
      dat["shipped"] = False
    return dat

  def get_ordered_datetime(self, raw=False):
    if not raw:
      ts = self.__ordered_datetime
      obj = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc)
      local_tz = pytz.timezone("Asia/Singapore")
      local_dt = local_tz.normalize(obj.astimezone(local_tz))
      return local_dt.strftime("%d/%m/%Y")
    else:
      return self.__ordered_datetime

  def get_customer_id(self):
    return self.__customer.get_id()

  def get_products(self):
    return self.__sales_list

  def get_id(self):
    return self.__id

class CartItem:
  def __init__(self, product_obj, quantity):
    self.product = product_obj
    self.quantity = quantity
    total = float(product_obj.retail_price) * quantity
    self.sub_total = str(round(total, 2))

  def __str__(self):
    return "{}x {}".format(self.quantity, self.product.get_title())


class Sale(CartItem):
  def __init__(self, id, product_obj, quantity, time_created):
    super().__init__(product_obj, quantity)
    self.__id = id
    self.__created_on = time_created

  def get_id(self):
    return self.__id

  def get_created_datetime(self, raw=False):
    if not raw:
      ts = self.__created_on
      obj = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc)
      local_tz = pytz.timezone("Asia/Singapore")
      local_dt = local_tz.normalize(obj.astimezone(local_tz))
      return local_dt.strftime("%d/%m/%Y")
    else:
      return self.__created_on

class Cart:
  def __init__(self, id, user_id, items):
    self.__id = id
    self.__user_id = user_id
    self.__item_list = items
    total = 0
    for x in items:
      total += float(x.sub_total)
    self.__total = str(round(total, 2))

  def get_id(self):
    return self.__id

  def clear(self):
    self.__item_list = []
    self.__total = 0

  def get_user(self):
    return self.__user_id

  def inventory_update(self):
    product_list = dat_loader.load_data("Products")["data"]
    item_list = self.__item_list
    for i, item in enumerate(item_list):
      for product in product_list:
        if item.product.get_id() == product.get_id():
          item.product = product
          item_list[i] = item
    self.__item_list = item_list

  def get_items(self):
    return self.__item_list

  def get_total(self):
    return self.__total
    
  def add_item(self, product_id, quantity):
    product_list = dat_loader.load_data("Products")["data"]
    item_list = self.__item_list
    counter = 0
    for product in product_list:
      if product.get_id() == product_id:
        if len(item_list) == 0:
          product_obj = product
          s = CartItem(product_obj, quantity)
          self.__item_list.append(s)
          total = float(self.__total)
          total += float(s.sub_total)
          self.__total = str(round(total, 2))
        else:
          counter2 = 0
          for item in item_list:
            if item.product.get_id() == product_id:
              c_q = item.quantity
              c_q += quantity
              self.update_item(product_id, c_q)
            else:
              counter2 += 1
          if counter2 == len(item_list):
            product_obj = product
            s = CartItem(product_obj, quantity)
            self.__item_list.append(s)
            total = float(self.__total)
            total += float(s.sub_total)
            self.__total = str(round(total, 2))
      else:
        counter += 1
    if counter == len(product_list):
      raise Exception("No such product")

  def update_item(self, product_id, new_quantity):
    item_list = self.__item_list
    product_list = dat_loader.load_data("Products")["data"]
    counter = 0
    for product in product_list:
      if product_id == product.get_id():
        try:
          for item in item_list:
            if item.product.get_id() == product_id:
              if new_quantity > item.quantity:
                diff = new_quantity - item.quantity
                item.quantity = new_quantity
                value = diff * float(item.product.retail_price)
                item_sub = float(item.sub_total)
                item_sub += value
                item.sub_total = str(round(item_sub, 2))
                total = float(self.__total)
                total += value
                self.__total = str(round(total, 2))
                self.__item_list = item_list
              elif new_quantity < item.quantity:
                diff = item.quantity - new_quantity
                item.quantity = new_quantity
                value = diff * float(item.product.retail_price)
                item_sub = float(item.sub_total)
                item_sub -= value
                item.sub_total = str(round(item_sub, 2))
                total = float(self.__total)
                total -= value
                self.__total = str(round(total, 2))
                self.__item_list = item_list
              else:
                pass
        except ValueError:
          raise Exception("Invalid quantity")
      else:
        counter += 1
    if counter == len(product_list):
      raise Exception("No such product")

  def remove_item(self, product_id):
    item_list = self.__item_list
    product_list = dat_loader.load_data("Products")["data"]
    counter = 0
    for product in product_list:
      if product_id == product.get_id():
        try:
          for item in item_list:
            if item.product.get_id() == product_id:
              total = float(self.__total)
              total -= float(item.sub_total)
              self.__total = str(round(total, 2))
              index = item_list.index(item)
              del item_list[index]
              self.__item_list = item_list
        except ValueError:
          raise Exception("Invalid quantity")
      else:
        counter += 1
    if counter == len(product_list):
      raise Exception("No such product")