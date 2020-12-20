import time
from datetime import datetime
import pytz
from werkzeug.utils import secure_filename
import load_helper as dat_loader
from parsers import size_readable
import os
import random

class File:
  def __init__(self, id, file_path):
    self.__id = id
    self.__file_path = file_path

  def get_file_path(self):
    return self.__file_path

  def get_id(self):
    return self.__id

  def get_link(self):
    link = "/getfile/{}/".format(self.__id)
    return link

class Photo(File):
  def __init__(self, id, file_path):
    super().__init__(id, file_path)


class Attached_File(File):
  def __init__(self, id, filename, file_path, file_type, file_size, uploaded_by):
    super().__init__(id, file_path)
    self.__filename = filename
    self.__uploaded_on = time.time()
    self.__file_type = file_type
    self.__file_size = file_size
    self.__uploaded_by = uploaded_by

  def get_uploaded_on(self, raw=False):
    if not raw:
      obj = datetime.utcfromtimestamp(self.__uploaded_on).replace(tzinfo=pytz.utc)
      local_tz = pytz.timezone("Asia/Singapore")
      local_dt = local_tz.normalize(obj.astimezone(local_tz))
      datetime_str = local_dt.strftime("%d/%m/%Y")
      return datetime_str
    else:
      return self.__uploaded_on

  def get_uploaded_by(self):
    return self.__uploaded_by

  def get_file_data(self):
    return {"file_type": self.__file_type, "file_size": self.__file_size}

  def get_filename(self):
    return self.__filename

upload_folder = ".\\uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpeg", "docx", "jpg"}


def allowed_file(filename):
  return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def upload(f, public=True, uploaded_by=None):
  if allowed_file(f.filename):
    filename = secure_filename(f.filename)
    file_path = os.path.join(upload_folder, filename)
    while True:
      if os.path.exists(file_path):
        file_name = filename.rsplit(".")
        name = file_name[0]
        name += str(random.randint(1, 1000))
        new_f_name = [name, file_name[1]]
        new_filename = ".".join(new_f_name)
        file_path = os.path.join(upload_folder, new_filename)
      else:
        break
    f.save(file_path)
    file_type = f.filename.rsplit('.', 1)[1].lower()
    file_size = size_readable(os.path.getsize(file_path))
    file_dat = dat_loader.load_data("Files")
    file_id = file_dat["id"]
    if public:
      f_obj = Photo(file_id, file_path)
    else:
      f_obj = Attached_File(file_id, filename, file_path, file_type, file_size, uploaded_by)
    file_list = file_dat["data"]
    file_list.append(f_obj)
    dat_loader.write_data("Files", file_list)
    if not public:
      return f_obj
    else:
      return f_obj.get_link()
  else:
    raise ValueError("Invalid file type")