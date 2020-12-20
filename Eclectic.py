from flask import request, redirect, jsonify, make_response, Response
from flask import Flask, render_template, send_file, abort, url_for
from send_mail import Mail
import report
from file import Photo, Attached_File, upload
from users import Staff, Customer, Address
from session import Pass_token, Session
from ticket import Ticket, Message
from order import Sale, Order
from session_mgmt import is_authenticated, get_user, is_staff, session_end, refresh_session
import load_helper as dat_loader
from forms import RegistrationForm, ForgetPasswordForm, PasswordResetForm, LoginForm, CreateProduct, FileUploadForm, \
  AddCart, AccountPasswordChange, NewTicketForm, AccountAddressChange, NewMessageForm
from product import Product
import stripe
import time
import re
from honeybadger import honeybadger
honeybadger.configure(api_key="300e2966")


app = Flask(__name__)

app.config["SECRET_KEY"] = "u3TpMdYxm2RncN7VTrTD8GycHq6BpYfPqkwdSwT5UBz6Uyzkm4g2CxrTBT6kVc7TvFbw8n8aKrarJb98sp5mbMjHvc"
app.config["STRIPE_SECRET"] = "sk_test_dc5NYOqosrlmJqpC8wS3A4XK00PRPwGUnH"
app.config["STRIPE_PUBLIC"] = "pk_test_TTKhfH0AEyWBHKxIRoiL24HK009XQKg3y2"


# Routing for Home Page
@app.route("/")
def home():
  return render_template("home/home.html")


# Routing for product page before login
@app.route("/products/")
def view_products():
  query = request.args.get("search")
  if query is None:
    products = dat_loader.load_data("Products")["data"]
    return render_template("home/view_products.html", products=products)
  else:
    products = dat_loader.load_data("Products")["data"]
    search_results = []
    for product in products:
      if query.upper() in product.get_title().upper() or query.upper() in product.get_description().upper():
        search_results.append(product)
    return render_template("home/search_products.html", products=search_results)


# Serve uploaded files
@app.route("/getfile/<int:id>/")
def get_file(id):
  file_list = dat_loader.load_data("Files")["data"]
  if len(file_list) == 0:
    abort(404)
  counter = 0
  for x in file_list:
    if x.get_id() == id and isinstance(x, Photo):
      return send_file(x.get_file_path())
    elif x.get_id() == id and is_authenticated(request) and isinstance(x, Attached_File):
      user = get_user(request)
      ticket_list = dat_loader.load_data("Tickets")["data"]
      m_list = []
      for ticket in ticket_list:
        if ticket.created_by.get_id() == user.get_id():
          m_list += ticket.get_messages()
      f_list = []
      for message in m_list:
        m1_list = message.get_files()
        for file in m1_list:
          f_list.append(file)
      if x.get_uploaded_by().get_id() == user.get_id() or isinstance(user, Staff):
        return send_file(x.get_file_path())
      else:
        count = 0
        for file in f_list:
          if file.get_id() == x.get_id():
            return send_file(x.get_file_path())
          else:
            count += 1
        if count == len(f_list):
          return abort(403)
    elif x.get_id() == id and not is_authenticated(request) and isinstance(x, Attached_File):
      return abort(403)
    else:
      counter += 1
  if counter == len(file_list):
    return abort(404)


# Product Details
@app.route("/products/<int:id>/")
def product_detail(id):
  products = dat_loader.load_data("Products")["data"]
  for product in products:
    if product.get_id() == id:
      return render_template("home/product_details.html", product=product)
  return abort(404)


# Routing for login page
@app.route("/login/", methods=["GET", "POST"])
def login():
  if is_authenticated(request):
    return redirect("/dashboard/")
  else:
    form = LoginForm()
    if request.method == "GET":
      form.username.data = ""
      form.password.data = ""
      return render_template("home/login.html", form=form)
    elif request.method == "POST" and form.validate_on_submit():
      username = form.username.data.lower()
      password = form.password.data
      user_list = dat_loader.load_data("Users")["data"]
      counter = 0
      for user in user_list:
        if isinstance(user, Customer) and user.email == username and user.Check_password(password):
          s = Session(user)
          s_dat = dat_loader.load_data("Session")["data"]
          s_dat.append(s)
          dat_loader.write_data("Session", s_dat, False)
          resp = make_response(redirect("/dashboard/"))
          resp.set_cookie("userID", str(user.get_id()))
          resp.set_cookie("sessionID", s.get_id())
          return resp
        elif isinstance(user, Staff) and user.get_staff_id() == username and user.Check_password(password):
          s = Session(user)
          s_dat = dat_loader.load_data("Session")["data"]
          s_dat.append(s)
          dat_loader.write_data("Session", s_dat, False)
          resp = make_response(redirect("/dashboard/"))
          resp.set_cookie("userID", str(user.get_id()))
          resp.set_cookie("sessionID", s.get_id())
          return resp
        else:
          counter += 1
    else:
      return abort(400)

# Routing for login page
@app.route("/api-service/login/validate/", methods=["GET", "POST"])
def login_validate():
  user_list = dat_loader.load_data("Users")["data"]
  counter = 0
  dat = request.get_json(force=True)
  for user in user_list:
    if isinstance(user, Customer) and user.email == dat["username"].lower() and user.Check_password(dat["password"]):
      return jsonify({"success": "true", "user": user.get_name()})
    elif isinstance(user, Staff) and user.get_staff_id() == dat["username"].lower() and user.Check_password(dat["password"]):
      return jsonify({"success": "true", "user":user.get_name()})
    else:
      counter += 1
  if counter == len(user_list):
    return jsonify({"success":"false", "message":"incorrect username/password."})

# Logout
@app.route("/logout/")
def logout():
  session_end(request)
  resp = make_response(redirect("/"))
  resp.set_cookie("userID", expires=0)
  resp.set_cookie("sessionID", expires=0)
  return resp


# Routing for register page - mine its here so might as well right
@app.route("/register/", methods=["POST", "GET"])
def register():
  form = RegistrationForm()
  if request.method == "POST":
    user_dat = dat_loader.load_data("Users")
    user_id = user_dat["id"]
    user_list = user_dat["data"]
    a = Address(form.address.data, form.postal.data, form.country.data, form.city.data)
    c1 = Customer(user_id, form.firstName.data, form.lastName.data, form.password.data, form.gender.data,
                  form.email.data.lower(), a, form.phoneNumber.data)
    user_list.append(c1)
    dat_loader.write_data("Users", user_list)
    return redirect("/login/")
  elif request.method == "GET":
    return render_template("home/register.html", form=form)

# Supporting register route - validate password
@app.route("/api-service/register/validate/password/", methods=["POST"])
def register_validate_password():
  dat = request.get_json(force=True)
  if dat["new"] == dat["confirm"]:
    return jsonify({"success":"true"})
  else:
    return jsonify({"success":"false", "message":"New passwords do not match"})

# Supporting register route - validate email
@app.route("/api-service/register/validate/email/", methods=["POST"])
def register_validate_email():
  dat = request.get_json(force=True)
  user_list = dat_loader.load_data("Users")["data"]
  e_list = []
  email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
  for user in user_list:
    e_list.append(user.email)
  if dat["data"] in e_list:
    return jsonify({"success": "false", "message": "Email already registered"})
  elif email_regex.fullmatch(dat["data"]):
    return jsonify({"success": "true"})
  else:
    return jsonify({"success": "false", "message": "Invalid email address"})


# Supporting register route - validate phone number
@app.route("/api-service/register/validate/number/", methods=["POST"])
def register_validate_number():
  dat = request.get_json(force=True)
  p_list = []
  user_list = dat_loader.load_data("Users")["data"]
  for user in user_list:
    p_list.append(user.contact_number)
  if dat["data"] in p_list:
    return jsonify({"success": "false", "message": "Your number cannot match with a existing user"})
  elif len(dat["data"]) != 8 or not dat["data"].isnumeric():
    return jsonify({"success": "false", "message": "Invalid phone number"})
  else:
    return jsonify({"success": "true"})

# Routing for Contact us page
@app.route("/contact_us/")
def contact_us():
  return render_template("home/contact_us.html")


# Routing for forget password page + reset password
# Token expires after a successful password reset OR 2 hours
@app.route("/forget/", methods=["GET", "POST"])
def forget():
  form_reset = PasswordResetForm()
  form_forget = ForgetPasswordForm()
  if form_forget.validate_on_submit():
    user_email = form_forget.email.data
    user_list = dat_loader.load_data("Users")["data"]
    customer_list = []
    for x in user_list:
      if isinstance(x, Customer):
        customer_list.append(x)
    for x in customer_list:
      if x.email == user_email:
        p_token = Pass_token(x.get_id())
        m1 = Mail()
        m1.content = f"""
        <!DOCTYPE html>
        <html lang="en">
          <body>
            <pre>
              Dear {x.get_name()},
        
              You have requested to reset your password for your Eclectic account. Copy or paste the link below to your
              browser or click on the link to reset your password. The link will expire after 2 hours.
              <a href="{p_token.get_link()}">{p_token.get_link()}</a>
        
              Warmest regards,
              Eclectic Support Team
            </pre>
          </body>
        </html>
        """
        m1.subject = "Eclectic Password Reset Link"
        m1.send(x.email)
        new_list = dat_loader.load_data("Tokens")["data"]
        new_list.append(p_token)
        dat_loader.write_data("Tokens", new_list, False)
    return redirect("/login/")
  elif request.args.get("auth") is None and not is_authenticated(request):
    return render_template("home/forget_password.html", form=form_forget)
  elif form_reset.validate_on_submit():
    user_id = int(form_reset.id.data)
    new_pass = form_reset.password1.data
    confirm_pass = form_reset.password2.data
    if new_pass == confirm_pass:
      user_list = dat_loader.load_data("Users")["data"]
      for x in user_list:
        if x.get_id() == user_id:
          x.Change_password(new_pass)
          dat_loader.write_data("Users", user_list, False)
          return redirect("/login/")
      auth_token = request.args.get("auth")
      token_list = dat_loader.load_data("Tokens")["data"]
      for x in token_list:
        trial = x.use(auth_token)
        if trial is None:
          pass
        else:
          form_reset.id.data = trial
          dat_loader.write_data("Tokens", token_list, False)
    else:
      return abort(400)
  elif not is_authenticated(request):
    auth_token = request.args.get("auth")
    token_list = dat_loader.load_data("Tokens")["data"]
    for x in token_list:
      trial = x.use(auth_token)
      if trial is None:
        pass
      else:
        form_reset.id.data = trial
        return render_template("home/new_password.html", form=form_reset)
    return redirect("/login/")


# Routing to dashboard after login
# will have logic to decide where to redirect users based on user type. Staff/Customer
@app.route("/dashboard/")
def after_login():
    if is_authenticated(request) and is_staff(request):
        return redirect("/dashboard/report/")
    elif is_authenticated(request) and not is_staff(request):
        return redirect("/dashboard/products/")
    else:
        return redirect("/login/")


# Routing for product page after login
@app.route("/dashboard/products/")  # - Customer
def dashboard_view_products():
  if is_authenticated(request) and not is_staff(request):
    refresh_session(request)
    query = request.args.get("search")
    if query is None:
      products = dat_loader.load_data("Products")["data"]
      return render_template("pages/customer_pages/products.html", products=products, user=get_user(request),
                             staff=is_staff(request))
    else:
      products = dat_loader.load_data("Products")["data"]
      search_results = []
      for product in products:
        if query.upper() in product.get_title().upper() or query.upper() in product.get_description().upper():
          search_results.append(product)
      return render_template("pages/customer_pages/search_products.html", products=search_results,
                             user=get_user(request), staff=is_staff(request))
  else:
    return redirect("/login/")


# Routing for product details page after login
@app.route("/dashboard/products/<int:id>/")  # - Customer
def dashboard_view_products_details(id):
  if is_authenticated(request) and not is_staff(request):
    refresh_session(request)
    products = dat_loader.load_data("Products")["data"]
    for product in products:
      if product.get_id() == id:
        return render_template("pages/customer_pages/products_details.html", product=product,
                               user=get_user(request), staff=is_staff(request))
    return abort(404)


# Routing for user management - staff
@app.route("/dashboard/users/")
def user_management():
  if is_authenticated(request) and is_staff(request):
    user_list = dat_loader.load_data("Users")["data"]
    results = []
    for user in user_list:
      if isinstance(user, Customer):
        results.append(user)
    return render_template("pages/staff_pages/user_management.html", users=results, user=get_user(request), staff=is_staff(request))
  elif is_authenticated(request) and not is_staff(request):
    return abort(403)
  else:
    return redirect("/login/")

# Supporting user management route - deactivate
@app.route("/api-service/user/deactivate/", methods=["POST"])
def user_deactivate():
  if is_authenticated(request) and is_staff(request):
    user_list = dat_loader.load_data("Users")["data"]
    dat = request.get_json(force=True)
    for user in user_list:
      if user.get_id() == int(dat["id"]):
        user_list.remove(user)
    dat_loader.write_data("Users", user_list)
    return jsonify({"success":"true"})
  elif is_authenticated(request) and not is_staff(request):
    return abort(403)
  else:
    return redirect("/login/")

# Routing for account management - customer/staff
@app.route("/dashboard/account/")
def user_account_management():
  if is_authenticated(request):
    return render_template("pages/account_settings.html", staff=is_staff(request), user=get_user(request))
  else:
    return redirect("/login/")

# Supporting account route - update phone number
@app.route("/api-service/account/update/number/", methods=["POST"])
def user_account_update_number():
  if is_authenticated(request):
    dat = request.get_json(force=True)
    c_user = get_user(request)
    user_list = dat_loader.load_data("Users")["data"]
    counter = 0
    number_list = []
    for user in user_list:
      number_list.append(user.contact_number)
    for user in user_list:
      if user.get_id() == c_user.get_id():
        if dat["data"] in number_list:
          return jsonify({"success":"false", "message":"Your number cannot match with a existing user"})
        elif len(dat["data"]) != 8 or not dat["data"].isnumeric():
          return jsonify({"success":"false", "message":"Invalid phone number"})
        else:
          user.contact_number = dat["data"]
          dat_loader.write_data("Users", user_list, False)
          return jsonify({"success":"true", "new_number":user.contact_number})
      else:
        counter += 1
    if counter == len(user_list):
      return abort(404)
  else:
    return abort(403)

# Supporting account route - update phone number
@app.route("/api-service/account/update/email/", methods=["POST"])
def user_account_update_email():
  if is_authenticated(request):
    dat = request.get_json(force=True)
    c_user = get_user(request)
    user_list = dat_loader.load_data("Users")["data"]
    e_list = []
    for user in user_list:
      e_list.append(user.email)
    counter = 0
    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    for user in user_list:
      if user.get_id() == c_user.get_id():
        if dat["data"] in e_list:
          return jsonify({"success":"false", "message":"Your email address cannot match with a existing user"})
        elif email_regex.fullmatch(dat["data"]):
          user.email = dat["data"]
          dat_loader.write_data("Users", user_list, False)
          return jsonify({"success": "true", "new_email": user.email})
        else:
          return jsonify({"success":"false", "message":"Invalid email address"})
      else:
        counter += 1
    if counter == len(user_list):
      return abort(404)
  else:
    return abort(403)

# Routing for account management password - customer/staff
@app.route("/dashboard/account/change-password/", methods=["GET", "POST"])
def customer_account_manage_pass():
  if is_authenticated(request):
    form = AccountPasswordChange()
    if request.method == "GET":
      return render_template("pages/account_settings_password.html", staff=is_staff(request), user=get_user(request), form=form)
    elif request.method == "POST" and form.validate_on_submit():
      c_user = get_user(request)
      user_list = dat_loader.load_data("Users")["data"]
      for user in user_list:
        if user.get_id() == c_user.get_id():
          user.Change_password(form.n_pass.data)
      dat_loader.write_data("Users", user_list, False)
      return redirect("/dashboard/account/")
  else:
    return redirect("/login/")

# Supporting account route - validate password
@app.route("/api-service/account/validate/password/", methods=["POST"])
def user_account_validate_password():
  if is_authenticated(request):
    dat = request.get_json(force=True)
    c_user = get_user(request)
    user_list = dat_loader.load_data("Users")["data"]
    counter = 0
    for user in user_list:
      if user.get_id() == c_user.get_id():
        if user.Check_password(dat["current"]) and dat["new"] == dat["confirm"]:
          return jsonify({"success":"true"})
        elif not user.Check_password(dat["current"]):
          return jsonify({"success":"false", "message":"Current password incorrect"})
        else:
          return jsonify({"success":"false", "message":"New passwords do not match"})
      else:
        counter += 1
    if counter == len(user_list):
      return abort(404)
  else:
    return abort(403)


# Routing for account management address - customer
@app.route("/dashboard/account/address/", methods=["POST", "GET"])
def customer_account_manage_address():
  if is_authenticated(request) and not is_staff(request):
    form = AccountAddressChange()
    if request.method == "GET":
      user = get_user(request)
      form.address.data = user.get_address_line()
      form.city.data = user.get_address_city()
      form.country.data = user.get_country()
      form.postal.data = user.get_address_postal()
      return render_template("pages/customer_pages/account_settings_address.html", form=form, staff=is_staff(request), user=user)
    elif request.method == "POST":
      c_user = get_user(request)
      user_list = dat_loader.load_data("Users")["data"]
      for user in user_list:
        if user.get_id() == c_user.get_id():
          user.set_address(form.address.data, form.postal.data, form.country.data, form.city.data)
      dat_loader.write_data("Users", user_list, False)
      return redirect("/dashboard/account/")
    else:
      return redirect("/dashboard/account/")
  elif is_authenticated(request) and is_staff(request):
    return abort(403)
  else:
    return redirect("/login/")


# Routing for inventory management - staff
@app.route("/dashboard/inventory/")
def view_inventory():
  if is_authenticated(request) and is_staff(request):
    products = dat_loader.load_data("Products")["data"]
    return render_template("pages/staff_pages/view_inventory.html", products=products, count=len(products),
                           user=get_user(request), staff=is_staff(request))
  else:
    return redirect("/login/")


# Routing for inventory management add - staff
@app.route("/dashboard/inventory/add/", methods=["GET", "POST"])
def add_inventory():
  if is_authenticated(request) and is_staff(request):
    form = CreateProduct()
    upload_image = FileUploadForm()
    if request.method == "GET":
      return render_template("pages/staff_pages/add_inventory.html", form=form, upload_image=upload_image,
                             user=get_user(request), staff=is_staff(request))
    elif request.method == "POST":
      image = upload_image.file.data
      image_link = upload(image)
      products = dat_loader.load_data("Products")["data"]
      products_id = dat_loader.load_data("Products")["id"]
      new_product = Product(products_id, form.title.data, form.description.data, int(form.stock.data),
                            form.retail_price.data, form.cost_price.data, image_link)
      products.append(new_product)
      dat_loader.write_data("Products", products)
      return redirect("/dashboard/inventory/")
  else:
    return redirect("/login/")


@app.route("/api-service/inventory/validate/", methods=["POST"])
def inventory_validate():
  if is_authenticated(request) and is_staff(request):
    dat = request.json
    product_list = dat_loader.load_data("Products")["data"]
    p_list = []
    for product in product_list:
      p_list.append(product.get_title())
    if dat["data"].strip() in p_list:
      return jsonify({"success":"false", "message":"New product's name matches existing product"})
    else:
      return jsonify({"success":"true"})
  else:
    return abort(403)


# Routing for inventory management update - staff
@app.route("/dashboard/inventory/update/<int:id>/", methods=["GET", "POST"])
def inventory_change(id):
  if is_authenticated(request) and is_staff(request):
    update_form = CreateProduct()
    if request.method == "POST":
      products = dat_loader.load_data("Products")["data"]
      for product in products:
        if product.get_id() == id:
          product.set_title(update_form.title.data)
          product.set_cost_price(update_form.cost_price.data)
          product.retail_price = update_form.retail_price.data
          product.set_description(update_form.description.data)
          product.stock = int(update_form.stock.data)
          dat_loader.write_data("Products", products, False)
          cart_list = dat_loader.load_data("Carts")["data"]
          for cart in cart_list:
            cart.inventory_update()
          dat_loader.write_data("Carts", cart_list, False)
      return redirect("/dashboard/inventory/")
    else:
      products = dat_loader.load_data("Products")["data"]
      for product in products:
        if product.get_id() == id:
          update_form.title.data = product.get_title()
          update_form.cost_price.data = product.get_cost_price()
          update_form.retail_price.data = product.retail_price
          update_form.description.data = product.get_description()
          update_form.stock.data = product.stock
          return render_template("pages/staff_pages/update_inventory.html", product=product, form=update_form,
                                 user=get_user(request), staff=is_staff(request))
  else:
    return redirect("/login/")


# Delete Product
@app.route("/dashboard/inventory/delete/<int:id>/", methods=["POST"])
def delete_product(id):
  if is_authenticated(request) and is_staff(request):
    products = dat_loader.load_data("Products")["data"]
    cart_list = dat_loader.load_data("Carts")["data"]
    for product in products:
      if product.get_id() == id:
        for cart in cart_list:
          cart_items = cart.get_items()
          for item in cart_items:
            if item.product.get_id() == id:
              cart.remove_item(id)
        dat_loader.write_data("Carts", cart_list, False)
        products.remove(product)
    dat_loader.write_data("Products", products)
    return redirect("/dashboard/inventory/")


# Routing for Ticket System - customer/staff
@app.route("/dashboard/support/")
def get_tickets():
  if is_authenticated(request):
    ticket_list = dat_loader.load_data("Tickets")["data"]
    user = get_user(request)
    results = []
    if request.args.get("closed") is None:
      for ticket in ticket_list:
        if ticket.get_staff_usr_id() == user.get_id() or ticket.created_by.get_id() == user.get_id():
          results.append(ticket)
          results.reverse()
          results.sort(key=lambda ticket_obj: ticket_obj.is_closed())
      return render_template("pages/support_ticket.html", staff=is_staff(request), user=user, tickets=results,
                             closed=None)
    elif request.args.get("closed") == "true":
      for ticket in ticket_list:
        if ticket.get_staff_usr_id() == user.get_id() and ticket.is_closed() or ticket.created_by.get_id() == user.get_id() and ticket.is_closed():
          results.append(ticket)
          results.reverse()
      return render_template("pages/support_ticket.html", staff=is_staff(request), user=user, tickets=results,
                             closed=True)
    elif request.args.get("closed") == "false":
      for ticket in ticket_list:
        if ticket.get_staff_usr_id() == user.get_id() and not ticket.is_closed() or ticket.created_by.get_id() == user.get_id() and not ticket.is_closed():
          results.append(ticket)
          results.reverse()
      return render_template("pages/support_ticket.html", staff=is_staff(request), user=user, tickets=results,
                             closed=False)
  else:
    return redirect("/dashboard/support/")


# Routing for Ticket system new - customer
@app.route("/dashboard/ticket/new/", methods=["POST", "GET"])
def new_ticket():
  if is_authenticated(request) and not is_staff(request):
    form = NewTicketForm()
    if request.method == "GET":
      return render_template("pages/customer_pages/ticket_create.html", staff=is_staff(request), user=get_user(request), form=form)
    elif request.method == "POST" and form.validate_on_submit():
      user = get_user(request)
      ticket_dat = dat_loader.load_data("Tickets")
      messages = []
      ticket_id = ticket_dat["id"]
      ticket_list = ticket_dat["data"]
      files = form.files.data
      uploaded_files = []
      if files[0].filename != "":
        for x in files:
          try:
            uploaded_files.append(upload(x, False, user))
          except ValueError:
            return abort(400)
      m_obj = Message(user, uploaded_files, form.description.data)
      messages.append(m_obj)
      t_obj = Ticket(ticket_id, user, form.subject.data, messages)
      ticket_list.append(t_obj)
      dat_loader.write_data("Tickets", ticket_list)
      return redirect("/dashboard/support/")
  elif is_authenticated(request) and is_staff(request):
    return abort(403)
  else:
    return redirect("/login/")


# Routing for Ticket detail - customer/staff
@app.route("/dashboard/ticket/<int:id>/", methods=["POST", "GET"])
def ticket_detail(id):
  if is_authenticated(request):
    user = get_user(request)
    form = NewMessageForm()
    ticket_list = dat_loader.load_data("Tickets")["data"]
    if request.method == "GET":
      count = 0
      for ticket in ticket_list:
        if ticket.get_id() == id:
          if ticket.get_staff_usr_id() == user.get_id() or ticket.created_by.get_id() == user.get_id():
            return render_template("pages/ticket_detail.html", ticket=ticket, user=user, staff=is_staff(request), form=form)
          else:
            return abort(403)
        else:
          count += 1
      if count == len(ticket_list):
        return abort(404)
    elif request.method == "POST" and form.validate_on_submit():
      for ticket in ticket_list:
        if ticket.get_id() == int(form.id.data):
          files = form.files.data
          uploaded_files = []
          if files[0].filename != "":
            for x in files:
              try:
                uploaded_files.append(upload(x, False, user))
              except ValueError:
                return abort(400)
            m1 = Message(user, uploaded_files, None)
          else:
            m1 = Message(user, [], form.message.data)
          ticket.add_new_reply(m1)
          dat_loader.write_data("Tickets", ticket_list, False)
          return redirect(url_for("ticket_detail", id=ticket.get_id()))
  else:
    return redirect("/login/")

# Supporting Ticket route - ticket close
@app.route("/api-service/ticket/close/", methods=["POST"])
def ticket_close():
  if is_authenticated(request):
    data = request.json
    ticket_id = int(data["id"])
    ticket_list = dat_loader.load_data("Tickets")["data"]
    for ticket in ticket_list:
      if ticket.get_id() == ticket_id:
        ticket.close()
    dat_loader.write_data("Tickets", ticket_list, False)
    return jsonify({"success":"true"})
  else:
    return abort(403)


# Routing for Cart - customer
@app.route("/dashboard/cart/")
def view_cart():
  if is_authenticated(request) and not is_staff(request):
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    for cart in cart_list:
      if cart.get_user() == user.get_id():
        return render_template("pages/customer_pages/view_cart.html", cart_total=cart.get_total(), user=get_user(request),
                               cart_items=cart.get_items(),
                               cart_size=len(cart.get_items()))
      else:
        counter += 1
    if counter == len(cart_list):
      return abort(500)
  else:
    return redirect("/login/")


# Supporting Cart route - cart remove item
@app.route("/api-service/cart/delete/", methods=["DELETE"])
def cart_api_delete():
  if is_authenticated(request) and not is_staff(request):
    json_dat = request.get_json(force=True)
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    for cart in cart_list:
      if cart.get_user() == user.get_id():
        product_id = int(json_dat["id"])
        cart.remove_item(product_id)
        dat_loader.write_data("Carts", cart_list, False)
        return Response(status=200)
      else:
        counter += 1
    if counter == len(cart_list):
      return abort(500)

# Supporting Cart route - cart update
@app.route("/api-service/cart/update/", methods=["POST"])
def cart_api_update():
  if is_authenticated(request) and not is_staff(request):
    json_dat = request.get_json(force=True)
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    for cart in cart_list:
      if cart.get_user() == user.get_id():
        for x in json_dat:
          q = int(x["quantity"])
          product_id = int(x["id"])
          cart.update_item(product_id, q)
        dat_loader.write_data("Carts", cart_list, False)
        return Response(status=200)
      else:
        counter += 1
    if counter == len(cart_list):
      return abort(500)
  else:
    return abort(403)

# Supporting Cart route - checkout + cart confirm
@app.route("/api-service/cart/confirm/", methods=["POST"])
def cart_api_confirm():
  domain_name = "http://127.0.0.1:5000"
  if is_authenticated(request) and not is_staff(request):
    json_dat = request.get_json(force=True)
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    for cart in cart_list:
      if cart.get_user() == user.get_id():
        for x in json_dat:
          q = int(x["quantity"])
          product_id = int(x["id"])
          cart.update_item(product_id, q)
        dat_loader.write_data("Carts", cart_list, False)
        item_list = cart.get_items()
        stripe_items = []
        for item in item_list:
          product = item.product
          item_img_list = []
          img_url = domain_name + product.pic_link
          item_img_list.append(img_url)
          item_price = int(float(product.retail_price) * 100)
          item_dict = {
            "name": product.get_title(),
            "description": product.get_description()[:100],
            "images": item_img_list,
            "amount": item_price,
            "currency": "sgd",
            "quantity": item.quantity
          }
          stripe_items.append(item_dict)
        stripe.api_key = app.config["STRIPE_SECRET"]
        session = stripe.checkout.Session.create(
          payment_method_types=["card"],
          line_items=stripe_items,
          success_url=domain_name + "/api-service/payment/success/",
          cancel_url=domain_name + "/checkout/cart/",
        )
        json_response = {
          "status": "ok",
          "id": session["id"]
        }
        return jsonify(json_response)
      else:
        counter += 1
    if counter == len(cart_list):
      return abort(500)
  else:
    return abort(403)


# Supporting Cart route - add to cart
@app.route("/api-service/cart/add/", methods=["POST"])
def cart_api_add():
  if is_authenticated(request) and not is_staff(request):
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    form = AddCart()
    if form.validate_on_submit():
      for cart in cart_list:
        if cart.get_user() == user.get_id():
          product_id = int(form.id.data)
          quantity = form.quantity.data
          cart.add_item(product_id, quantity)
        else:
          counter += 1
      if counter == len(cart_list):
        return abort(500)
      dat_loader.write_data("Carts", cart_list, False)
      return redirect("/dashboard/products/")



# Routing for Orders - customer
@app.route("/dashboard/orders/")
def view_orders():
  if is_authenticated(request) and not is_staff(request):
    user = get_user(request)
    results = []
    order_list = dat_loader.load_data("Orders")["data"]
    delivered = None
    if request.args.get("delivered") is None:
      for x in order_list:
        if x.get_customer_id() == user.get_id():
          results.append(x)
          results.reverse()
          results.sort(key=lambda order: order.is_shipped())
          results.sort(key=lambda order: not order.is_delivered())
          results.reverse()
    elif request.args.get("delivered") == "false":
      delivered = False
      for x in order_list:
        if x.is_shipped() and not x.is_delivered() and x.get_customer_id() == user.get_id():
          results.append(x)
          results.reverse()
    elif request.args.get("delivered") == "true":
      delivered = True
      for x in order_list:
        if x.is_delivered() and x.get_customer_id() == user.get_id():
          results.append(x)
          results.reverse()
    return render_template("pages/customer_pages/view_orders.html", orders=results, user=user,
                           delivered=delivered)
  else:
    return redirect("/login/")


# Supporting Order route - create Order object upon successful payment
@app.route("/api-service/payment/success/", methods=["GET"])
def order_api_create():
  if is_authenticated(request) and not is_staff(request):
    cart_list = dat_loader.load_data("Carts")["data"]
    user = get_user(request)
    counter = 0
    for cart in cart_list:
      if cart.get_user() == user.get_id():
        item_list = cart.get_items()
        sale_dat = dat_loader.load_data("Sales")
        sale_id = sale_dat["id"]
        sale_list = sale_dat["data"]
        order_sales = []
        total = 0
        product_list = dat_loader.load_data("Products")["data"]
        for item in item_list:
          product = item.product
          for obj in product_list:
            if obj.get_id() == product.get_id():
              obj.stock -= int(item.quantity)
          s = Sale(sale_id, product, item.quantity, time.time())
          sale_id += 1
          sale_list.append(s)
          order_sales.append(s)
          total += float(s.sub_total)
        cart.clear()
        order_dat = dat_loader.load_data("Orders")
        order_id = order_dat["id"]
        order_list = order_dat["data"]
        o = Order(order_id, order_sales, str(round(total, 2)), user, time.time())
        order_list.append(o)
        dat_loader.write_data("Sales", sale_list)
        dat_loader.write_data("Orders", order_list)
        dat_loader.write_data("Products", product_list, False)
        dat_loader.write_data("Carts", cart_list, False)
        return redirect("/dashboard/orders/")
      else:
        counter += 1
    if counter == len(cart_list):
      return abort(500)
  else:
    return abort(403)


# Routing for Orders detail - customer
@app.route("/dashboard/orders/<int:id>")
def orders_detail(id):
  if is_authenticated(request) and not is_staff(request):
    order_list = dat_loader.load_data("Orders")["data"]
    counter = 0
    for x in order_list:
      if x.get_id() == id:
        return render_template("pages/customer_pages/view_orders_detail.html", order=x, user=get_user(request))
      else:
        counter += 1
    if len(order_list) == counter:
      return abort(404)
  else:
    return redirect("/login/")


# Corn jobs
@app.route("/api-service/corn/", methods=["POST"])
def corn_jobs():
  if is_authenticated(request):
    refresh_session(request)
  return Response(status=200)


# Routing for Reports
@app.route("/dashboard/report/")
def dashboard_report():
    if is_authenticated(request) and is_staff(request):
        year_list = []
        profit_list = []
        total_profit = 0
        sale_product = {}
        product_sale = {}
        profit_margin_list = []


        sales = dat_loader.load_data("Sales")["data"]
        year_filter = request.args.get("year")

        # BarChart
        for sale in sales:
            # Year for the sales
            if sale.get_created_datetime()[-4:] not in year_list:
                year_list.append(sale.get_created_datetime()[-4:])
            year_list.sort()

            if year_filter is None:
                year_filter = year_list[-1]

            # Sales for the year selected
            if sale.get_created_datetime()[-4:] == year_filter:
                profit_list = report.profit(sale, profit_list)

            # Reformat the list
        profit_list = report.reformat_list(profit_list)

            # Finding Total Profit
        for profit in profit_list:
            total_profit += float(profit)
        total_profit = f'{total_profit:.2f}'

        legend_1 = 'Monthly Sales'
        labels_1 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December"]
        values_1 = profit_list

        # PieChart
        for sale in sales:
            if sale.get_created_datetime()[-4:] == year_filter:
                if sale.product.get_title() not in sale_product.keys():
                    sale_product[sale.product.get_title()] = report.calculate_profit(sale)
                    product_sale[sale.product.get_title()] = report.calculate_sale(sale)
                else:
                    sale_product[sale.product.get_title()] += report.calculate_profit(sale)
                    product_sale[sale.product.get_title()] += report.calculate_sale(sale)
        # Horizontal Bar CHart
                for key in sale_product:
                  profit_margin =  float((float(sale_product[key])/ float(product_sale[key]) ) * 100)
                  profit_margin_list.append(profit_margin)

        profit_margin_list = report.reformat_list(profit_margin_list)

        legend_2 = 'Sales Distribution'
        labels_2 =  list(sale_product.keys())
        values_2 =  report.reformat_list(list(sale_product.values()))

        legend_3 = 'Profit Margin for the year'
        labels_3 = list(product_sale.keys())
        values_3 = profit_margin_list

        return render_template("pages/staff_pages/view_report.html", user=get_user(request), staff=is_staff(request),
                               year_list=year_list,
                               values_1=values_1, labels_1=labels_1, legend_1=legend_1,
                               values_2=values_2, labels_2=labels_2, legend_2=legend_2,
                               values_3=values_3, labels_3=labels_3, legend_3=legend_3,
                               total_profit=total_profit, year_filter = year_filter
                               )
    else:
        return redirect("/login/")


# function to parse obj id for display
@app.context_processor
def utility_processor():
  def format_id(obj_id):
    return int(obj_id) + 1
  return dict(format_id=format_id)

if __name__ == "__main__":
  app.run(debug=True)
