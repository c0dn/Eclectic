import string
import random
import time

class Pass_token:
  def __init__(self, user_id):
    self.__id = 0
    self.__user = user_id
    char = string.ascii_letters + string.digits
    self.__auth_token = ''.join(random.choice(char) for i in range(72))
    self.__expire = time.time() + 7200
    self.__active = True

  def use(self, auth):
    c_time = time.time()
    if self.__expire > c_time and self.__active and auth == self.__auth_token:
      self.__active = False
      return self.__user
    else:
      return None

  def get_id(self):
    return self.__id

  def get_link(self):
    return "http://127.0.0.1:5000/forget/?auth={}".format(self.__auth_token)


class Session:
  def __init__(self, user_obj):
    self.__user = user_obj
    char = string.ascii_letters + string.digits
    self.__id = ''.join(random.choice(char) for i in range(72))
    self.__expire = time.time() + 1800
    self.__valid = True

  def get_id(self):
    return self.__id

  def get_user_id(self):
    return self.__user.get_id()

  def get_user(self):
    return self.__user

  def refresh(self):
    expire = self.__expire
    c_time = time.time()
    if expire > c_time and self.__valid:
      self.__expire = expire + 1800
    else:
      self.__valid = False

  def check(self):
    c_time = time.time()
    if self.__expire > c_time and self.__valid:
      return True
    elif self.__expire < c_time:
      self.__valid = False
      return False
    else:
      return False

  def logout(self):
    self.__valid = False
