from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class AddCafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    map_url = StringField("Cafe Location URL", validators=[DataRequired(), URL()])
    seats = StringField("Seats", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price Eg. $2.2", validators=[DataRequired()])
    has_toilet = BooleanField("Are there toilets")
    has_wifi = BooleanField("Is there WiFi")
    has_sockets = BooleanField("Are there sockets")
    can_take_calls = BooleanField("Can the cafe be contacted")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
