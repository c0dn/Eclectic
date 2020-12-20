from datetime import datetime
import time
import pytz
import load_helper as dat_loader
from users import Staff

class Message:
  def __init__(self, sent_by, file_list, content):
    # files need to be a list
    self.sent_by = sent_by
    self.content = content
    self.__attached_files = file_list
    self.__sent_on = time.time()

  def get_sent_on(self, raw=False):
    if not raw:
      obj = datetime.utcfromtimestamp(self.__sent_on).replace(tzinfo=pytz.utc)
      local_tz = pytz.timezone("Asia/Singapore")
      local_dt = local_tz.normalize(obj.astimezone(local_tz))
      datetime_str = local_dt.strftime("%H:%M %d/%m/%Y")
      return datetime_str
    else:
      return self.__sent_on

  def get_files(self):
    return self.__attached_files

class Ticket:
  def __init__(self, id, created_by, subject, message_list):
    # messages must be a list
    self.__id = id
    self.created_by = created_by
    self.subject = subject
    self.__message_list = message_list
    self.__closed = False
    self.__created_on = time.time()
    # Assign ticket to a staff
    user_list = dat_loader.load_data("Users")["data"]
    count_list = []
    for user in user_list:
      if isinstance(user, Staff):
        count_list.append(user.customer_count)
    min_c = min(count_list)
    for user in user_list:
      if isinstance(user, Staff):
        if user.customer_count == min_c:
          self.__assigned_to = user
          user.customer_count += 1
          break
    dat_loader.write_data("Users", user_list, False)

  def get_id(self):
    return self.__id

  def get_staff_usr_id(self):
    return self.__assigned_to.get_id()

  def get_created_on(self):
    obj = datetime.utcfromtimestamp(self.__created_on).replace(tzinfo=pytz.utc)
    local_tz = pytz.timezone("Asia/Singapore")
    local_dt = local_tz.normalize(obj.astimezone(local_tz))
    datetime_str = local_dt.strftime("%d/%m/%Y")
    return datetime_str

  def get_messages(self):
    return self.__message_list[1:]

  def is_closed(self):
    return self.__closed

  def get_last_reply(self):
    last_obj = self.__message_list[-1]
    last_reply = last_obj.content
    return last_reply

  def get_last_sent(self):
    last_obj = self.__message_list[-1]
    last_person = last_obj.sent_by.get_name()
    return last_person

  def get_last_datetime(self):
    last_obj = self.__message_list[-1]
    last_person = last_obj.get_sent_on()
    return last_person

  def get_first_msg(self):
    first_obj = self.__message_list[0]
    first_msg = first_obj.content
    return first_msg

  def get_first_files(self):
    first_obj = self.__message_list[0]
    first_msg = first_obj.get_files()
    return first_msg

  def close(self):
    self.__closed = True

  def add_new_reply(self, message):
    message_list = self.__message_list
    message_list.append(message)
    self.__message_list = message_list