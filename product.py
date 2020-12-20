from parsers import identify_product, extract_info
import nltk

class Product:
  mappings = {"NFC": "near-field-communication",
              "bluetooth": "Bluetooth",
              "mAh": "milliamp Hour",
              "OSI": "Optical Image Stabilization",
              }

  def __init__(self, id, title, description, stock, retail_price, cost_price, pic_link):
    self.__id = id
    self.__title = title
    self.__description = description
    self.pic_link = pic_link
    self.stock = stock
    self.retail_price = retail_price
    self.__cost_price = cost_price
    self.__product_attributes = self.gen_attr()

  def gen_attr(self):
    attributes = {
      "type": identify_product(self.__title),
    }
    sentences = nltk.sent_tokenize(self.__description)
    attributes["attrs"] = extract_info(sentences, attributes["type"], self.__class__.mappings)
    return attributes

  def set_description(self, description):
    self.__description = description
    self.__product_attributes = self.gen_attr()

  def set_title(self, title):
    self.__title = title
    self.__product_attributes = self.gen_attr()

  def set_cost_price(self, cost_price):
    self.__cost_price = cost_price

  def get_description(self):
    return self.__description

  def get_attr(self):
    return self.__product_attributes

  def get_title(self):
    return self.__title

  def get_cost_price(self):
    return self.__cost_price

  def get_id(self):
    return self.__id