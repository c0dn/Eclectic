from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.fields import PasswordField, SubmitField, HiddenField, StringField, SelectField, TextAreaField, \
    IntegerField, MultipleFileField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField
import pycountry


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Some country's name are too long
        c = []
        for country in pycountry.countries:
            if len(country.name) < 20:
                t = (country.name, country.name)
                c.append(t)
        self.choices = c


class ForgetPasswordForm(FlaskForm):
    email = StringField("Email address", [DataRequired()])
    submit_btn = SubmitField("Submit")


class PasswordResetForm(FlaskForm):
    id = HiddenField("user_id", [DataRequired()])
    password1 = PasswordField("New Password", [DataRequired()])
    password2 = PasswordField("Confirm New Password", [DataRequired()])
    submit_btn = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Email/Staff ID", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit_btn = SubmitField("Submit")


class FileUploadForm(FlaskForm):
    file = FileField("Attach file")


class RegistrationForm(FlaskForm):
    firstName = StringField("First Name", [Length(min=1, max=150), DataRequired()])
    lastName = StringField("Last Name", [Length(min=1, max=150), DataRequired()])
    phoneNumber = StringField("Phone Number:", [Length(min=8, max=8), DataRequired()])
    gender = SelectField("Gender", [DataRequired()], choices=[("", "Select"), ("F", "Female"), ("M", "Male")],
                         default="")
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    confirm = PasswordField("Confirm Password ",
                            [DataRequired(), EqualTo("password", message="Passwords must be the same")])
    address = StringField("Address", [DataRequired()])
    postal = StringField("Postal code", [DataRequired()])
    country = CountrySelectField("Country", [DataRequired()])
    city = StringField("City", [DataRequired()])
    submit_btn = SubmitField("Submit")


class CreateProduct(FlaskForm):
    title = StringField("Title", [DataRequired()])
    stock = StringField("Stock", [DataRequired()])
    cost_price = StringField("Cost Price", [DataRequired()])
    retail_price = StringField("Retail Price", [DataRequired()])
    description = TextAreaField("Description", [DataRequired()])
    submit_btn = SubmitField("Submit")
    
class AccountPasswordChange(FlaskForm):
    c_pass = PasswordField("Current Password", [DataRequired()])
    n_pass = PasswordField("New Password", [DataRequired()])
    nc_pass = PasswordField("Confirm New Password", [DataRequired(), EqualTo("n_pass", message='Passwords must be the same')])
    submit_btn = SubmitField("Submit")

class AccountAddressChange(FlaskForm):
    address = StringField("Address", [DataRequired()])
    city = StringField("City", [DataRequired()])
    postal = StringField("Postal code", [DataRequired()])
    country = CountrySelectField("Country", [DataRequired()])
    submit_btn = SubmitField("Submit", [DataRequired()])


class AddCart(FlaskForm):
    id = HiddenField("product_id", [DataRequired()])
    quantity = IntegerField("Quantity : ", [DataRequired()])

    class Meta:
        csrf = False

class NewTicketForm(FlaskForm):
    subject = StringField("Subject", [DataRequired()])
    files = MultipleFileField("Attach file")
    description = TextAreaField("Description", [DataRequired()])
    submit_btn = SubmitField("Submit")

class NewMessageForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField("ticket_id", [DataRequired()])
    message = StringField("Message")
    files = MultipleFileField("Attach file")
    submit_btn = SubmitField("Submit")