# TODO: ADD A RATING SYSTEM FOR ONLY LOGGED IN USERS
# TODO: 9.ALLOW USERS TO FILTER OUT BASED ON SOME SPECIFIC DETAILS
# TODO: 10.HOST THE SITE ON HEROKU
# TODO: 11.CAFES SHOULD BE DISPLAYED ON THE HOME PAGE BASED ON RATINGS

from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import AddCafeForm, RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from random import choice
import os

open_times = ["8:00 - 20:00", "7:00 - 19:00", "24 Hours", "8:00 - 17:00", "7:30 - 19:30"]
cafe_ratings = ["4.2", "4.9", "3.7", "4.3", "4.5", "4.1"]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///cafe_db.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

user_login = LoginManager()
user_login.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    owner_id = db.Column(db.Integer, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)


db.create_all()


@user_login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    cafe_list = db.session.query(Cafe).all()
    return render_template("home_page.html", cafe_list=cafe_list, logged_in=current_user.is_authenticated, open_times=choice(open_times))


@app.route("/cafe/<int:cafe_id>", methods=["GET", "POST"])
def cafe_page(cafe_id):
    requested_cafe = Cafe.query.get(cafe_id)
    if current_user.is_authenticated:
        owner_id = current_user.id
    else:
        owner_id = None
    link = map_link(requested_cafe.name, requested_cafe.location)
    print(link)
    return render_template("cafe_page.html", r_cafe=requested_cafe, logged_in=current_user.is_authenticated, owner_id=owner_id, link=link, open_times=choice(open_times), cafe_ratings=choice(cafe_ratings))


@app.route("/add-cafe", methods=["GET", "POST"])
@login_required
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_toilet=int(form.has_toilet.data),
            has_wifi=int(form.has_wifi.data),
            seats=form.seats.data,
            can_take_calls=int(form.can_take_calls.data),
            has_sockets=int(form.has_sockets.data),
            coffee_price=form.coffee_price.data,
            owner_id=current_user.id
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST"])
@login_required
def edit_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    edit_form = AddCafeForm(
        name=cafe.name,
        location=cafe.location,
        img_url=cafe.img_url,
        map_url=cafe.map_url,
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.location = edit_form.location.data
        cafe.img_url = edit_form.img_url.data
        cafe.map_url = edit_form.map_url.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data
        cafe.has_toilet = int(edit_form.has_toilet.data)
        cafe.has_sockets = int(edit_form.has_sockets.data)
        cafe.has_wifi = int(edit_form.has_wifi.data)
        cafe.can_take_calls = int(edit_form.can_take_calls)
        return redirect(url_for("cafe_page", cafe_id=cafe_id))

    return render_template("add.html", cafe_id=cafe_id, form=edit_form, logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("This email already exists. Please login instead", "danger")
            return redirect(url_for("login"))
        else:
            new_user = User(
                email=form.email.data,
                password=generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Your password is incorrect. Please try again", "danger")
                return redirect(url_for("login"))
        else:
            flash("This email is not registered. Please try again or sign up", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/delete/<int:cafe_id>")
@login_required
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


def map_link(name, loc):
    name_list = "%20".join((name + " " + loc).split()).replace("&", "and")
    print(name_list)
    link = f"https://maps.google.com/maps?q={name_list}&t=&z=13&ie=UTF8&iwloc=&output=embed"
    return link


if __name__ == "__main__":
    app.run(debug=True)
