import os
import hashlib
import binascii
from order import Cart
import load_helper as dat_loader

class Address:
  def __init__(self, address, postal, country, city):
    self.address = address
    self.postal = postal
    self.country = country.capitalize()
    self.city = city

  def get_full_address(self):
    return self.address + " " + self.country + " " + self.postal


class User:
  def __init__(self, id, first_name, last_name, password, gender, contact, email):
    self.__id = id
    self.first_name = first_name
    self.email = email
    self.contact_number = contact
    self.last_name = last_name
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    p_hash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"),
                                  salt, 100000)
    p_hash = binascii.hexlify(p_hash)
    self.__password = (salt + p_hash).decode("ascii")
    self.gender = gender
    self.is_authenticated = False

  def Change_password(self, new_pass):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    p_hash = hashlib.pbkdf2_hmac("sha512", new_pass.encode("utf-8"), salt, 100000)
    p_hash = binascii.hexlify(p_hash)
    self.__password = (salt + p_hash).decode("ascii")

  def Check_password(self, password):
    salt = self.__password[:64]
    stored_password = self.__password[64:]
    p_hash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt.encode("ascii"), 100000)
    p_hash = binascii.hexlify(p_hash).decode("ascii")
    if p_hash == stored_password:
      self.is_authenticated = True
      return True
    else:
      return False

  def get_name(self):
    return self.first_name + ' ' + self.last_name

  def get_id(self):
    return self.__id


class Customer(User):
  def __init__(self, id, first_name, last_name, password, gender, email, address, contact):
    super().__init__(id, first_name, last_name, password, gender, contact, email)
    self.__address = address
    # Customer's cart creation
    cart_dat = dat_loader.load_data("Carts")
    cart_id = cart_dat["id"]
    cart_list = cart_dat["data"]
    c = Cart(cart_id, id, [])
    cart_list.append(c)
    dat_loader.write_data("Carts", cart_list)

  def set_address(self, address, postal, country, city):
    new_a = Address(address, postal, country, city)
    self.__address = new_a

  def get_address(self):
    return self.__address.get_full_address()

  def get_address_postal(self):
    return self.__address.postal

  def get_address_line(self):
    return self.__address.address

  def get_address_city(self):
    return self.__address.city

  def get_country(self):
    return self.__address.country


class Staff(User):
  def __init__(self, id, staff_id, first_name, last_name, password, gender, contact, email):
    super().__init__(id, first_name, last_name, password, gender, contact, email)
    self.__staff_id = staff_id
    self.customer_count = 0

  def get_staff_id(self):
    return self.__staff_id