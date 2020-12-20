import shelve
import dbm

def load_data(dict_key: str):
  dat = {}
  try:
    with shelve.open("data", "r") as db:
      dat["data"] = db[dict_key]
      class_ids = db["ids"]
      dat["id"] = int(class_ids[dict_key]) + 1
      if len(dat["data"]) != 0:
        last_obj = dat["data"][-1]
        if last_obj.get_id() == dat["id"]:
          dat["id"] += 1
      else:
        dat["id"] = 0
  except KeyError:
    with shelve.open("data", "w") as db:
      db[dict_key] = []
      dat["data"] = []
      dat["id"] = 0
      class_ids = db["ids"]
      class_ids[dict_key] = -1
      db["ids"] = class_ids
  except dbm.error[0]:
    with shelve.open("data", "c") as db:
      db[dict_key] = []
      dat["data"] = []
      dat["id"] = 0
      db["ids"] = {dict_key:-1}
  return dat

def write_data(dict_key: str, new_dat: list, update_id=True):
  try:
    with shelve.open("data", "w") as db:
      db[dict_key] = new_dat
      if update_id:
        class_ids = db["ids"]
        if len(new_dat) != 0:
          last_obj = new_dat[-1]
          class_ids[dict_key] = last_obj.get_id() - 1
          db["ids"] = class_ids
        else:
          class_ids[dict_key] = -1
          db["ids"] = class_ids
  except dbm.error[0]:
    with shelve.open("data", "c") as db:
      db[dict_key] = new_dat
      new_id = len(new_dat) - 1
      db["ids"] = {dict_key:new_id}
  except KeyError:
    with shelve.open("data", "w") as db:
      new_id = len(new_dat) - 1
      class_ids = db["ids"]
      class_ids[dict_key] = new_id
      db["ids"] = class_ids
      db[dict_key] = new_dat
