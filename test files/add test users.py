from load_helper import load_data, write_data
from users import Customer, Staff, Address
import requests
import json
import random

# Add test Staff & Customer to db
# Login details
# Staff 1 - will_staff:password
# Staff 2 - dy_staff:password
# Customer 1 - joelpeh2002@xrpmail.com:password
user_dat = load_data("Users")
user_id = user_dat["id"]
s1 = Staff(user_id, "will_staff", "William", "Oon", "password", "Male", "98362626", "williamoon2@gmail.com")
user_id += 1
s2 = Staff(user_id, "dy_staff", "Dylan", "Liew", "password", "Male", "94956325", "dylan12912@gmail.com")
user_id += 1
a = Address("2 Ang Mo Kio Street 44", "569250", "Singapore", "Singapore")
c = Customer(user_id, "Joel", "Peh", "password", "Male", "joelpeh2002@xrpmail.com", a, "98283783")
r = requests.get("https://randomuser.me/api/?inc=location,name,email,gender&results=9&nat=us")
dat = json.loads(r.text)["results"]
user_id += 1
user_list = [s1, s2, c]
for x in dat:
  p_number = ["9"]
  for y in range(0, 7):
    p_number.append(str(random.randint(0, 9)))
  phone_number = "".join(p_number)
  address_dat = x["location"]
  street_dat = address_dat["street"]
  address = str(street_dat["number"]) + " " + street_dat["name"]
  postal_code = str(address_dat["postcode"]) + str(random.randint(0,9))
  name_dat = x["name"]
  a = Address(address, postal_code, "Singapore", "Singapore")
  c = Customer(user_id, name_dat["first"], name_dat["last"], "password", x["gender"].capitalize(), x["email"], a, phone_number)
  user_list.append(c)

write_data("Users", user_list)