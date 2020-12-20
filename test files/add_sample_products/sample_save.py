from file import Photo
from product import Product
import load_helper as dat_loader
import os

with open("sample_earbuds.txt", "r") as file:
	p1_desc = file.read()
with open("sample_headphones.txt", "r") as file:
	p2_desc = file.read()
with open("sample_laptop.txt", "r") as file:
	p3_desc = file.read()
with open("sample_phone1.txt", "r") as file:
	p4_desc = file.read()
with open("sample_phone2.txt", "r") as file:
	p5_desc = file.read()
with open("sample_TV.txt", "r") as file:
	p6_desc = file.read()
with open("sample_powerbank.txt", "r") as file:
	p7_desc = file.read()

base_path = ".\\uploads"
p_list = []
def upload(filename):
	file_path = os.path.join(base_path, filename)
	file_dat = dat_loader.load_data("Files")
	file_id = file_dat["id"]
	file_list = file_dat["data"]
	f_obj = Photo(file_id, file_path)
	file_list.append(f_obj)
	dat_loader.write_data("Files", file_list)
	return f_obj.get_link()


p1 = Product(0, "Eclectic TWS earbuds", p1_desc, 20, "250", "40", upload("earbuds.jpg"))
p2 = Product(1, "Eclectic headphone", p2_desc, 10, "105.99", "30", upload("headphone.jpg"))
p3 = Product(2, "Eclectic gaming laptop", p3_desc, 5, "4109.99", "3000", upload("laptop.jpeg"))
p4 = Product(3, "Eclectic F9 smartphone", p4_desc, 40, "1800", "550", upload("f9.jpg"))
p5 = Product(4, "Eclectic C6 smartphone", p5_desc, 20, "1000", "200", upload("c6.jpg"))
p6 = Product(5, "Eclectic TV 65''", p6_desc, 10, "4000", "2300", upload("TV.jpg"))
p7 = Product(6, "20000 mAh Eclectic powerbank", p7_desc, 200, "54.99", "20", upload("powerbank.jpg"))

p_list.append(p1)
p_list.append(p2)
p_list.append(p3)
p_list.append(p4)
p_list.append(p5)
p_list.append(p6)
p_list.append(p7)

for x in p_list:
	print("%s: %s" %(x.get_title(), x.pic_link))
	
dat_loader.write_data("Products", p_list)
