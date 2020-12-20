import load_helper as dat_loader
from users import Customer, Staff

user_list = dat_loader.load_data("Users")["data"]
for user in user_list:
  if isinstance(user, Customer):
    print(f"{user.email}:password")
  elif isinstance(user, Staff):
    print(f"{user.get_staff_id()}:password")