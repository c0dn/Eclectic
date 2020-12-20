import load_helper as dat_loader
from ticket import Ticket, Message
from file import Attached_File
from werkzeug.utils import secure_filename
from parsers import size_readable
from users import Customer
import random
import os

upload_folder = ".\\uploads"

def upload_attached(filename, user_obj):
  filename = secure_filename(filename)
  file_path = os.path.join(upload_folder, filename)
  file_type = filename.rsplit('.', 1)[1].lower()
  file_size = size_readable(os.path.getsize(file_path))
  file_dat = dat_loader.load_data("Files")
  file_id = file_dat["id"]
  f_obj = Attached_File(file_id, filename, file_path, file_type, file_size, user_obj)
  file_list = file_dat["data"]
  file_list.append(f_obj)
  dat_loader.write_data("Files", file_list)
  return f_obj

user_list = dat_loader.load_data("Users")["data"]
ticket_dat = dat_loader.load_data("Tickets")
ticket_id = ticket_dat["id"]
ticket_list = ticket_dat["data"]
cus = user_list[2]
staff = user_list[0]

# Ticket 1 create
m1 = Message(cus, [], "Hi I got problem")
m2 = Message(staff, [], "Hi! May I know the issue you are facing?")
m3 = Message(cus, [], "You see the color here not white")
m4 = Message(cus, [upload_attached("help2.png", cus)], None)
messages = [m1, m2, m3, m4]
t1 = Ticket(ticket_id, cus, "Problem with the Eclectic earbuds", messages)
ticket_list.append(t1)

# Ticket 2 create
ticket_id += 1
files = [upload_attached("help3.png", cus), upload_attached("help1.png", cus)]
m5 = Message(cus, files, "Hi isn't it suppose to be white?")
messages = [m5]
t2 = Ticket(ticket_id, cus, "Did I get scam?", messages)
ticket_list.append(t2)

# Ticket 3 create
ticket_id += 1
files = [upload_attached("help4.png", cus)]
m6 = Message(cus, files, "Problem with right side")
m7 = Message(staff, [], "Hi, You can try and reset your earbuds by holding down the button at the back for 10 seconds")
messages = [m6, m7]
t3 = Ticket(ticket_id, cus, "Help", messages)
ticket_list.append(t3)

dat_loader.write_data("Tickets", ticket_list)